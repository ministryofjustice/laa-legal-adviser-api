# coding=utf-8
import csv
import itertools
import logging
import os
import re
import time
import tempfile
from django.db.utils import ProgrammingError
import xlrd

from billiard.exceptions import SoftTimeLimitExceeded
from celery.exceptions import Ignore
from celery import group
from celery import Task
from django.core.cache import cache
from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import connection, transaction
from django.utils.text import slugify

from . import models
from . import geocoder
from laalaa.celery import app


logging.basicConfig(filename="adviser_import.log", level=logging.WARNING)


# Python 3 compatibility
try:
    unicode("")  # Python 2
except NameError:
    unicode = str  # Python 3
try:
    xrange  # Python 2
except NameError:
    xrange = range  # Python 3
try:
    basestring  # Python 2
except NameError:
    basestring = str  # Python 3


def to_key(postcode):
    return re.sub("[^0-9A-Z]+", "", postcode)


def geocode(postcode):
    loc = models.Location.objects.filter(postcode=postcode, point__isnull=False)
    if len(loc):
        point = loc[0].point
    else:
        result = geocoder.geocode(postcode)
        point = Point(result.longitude, result.latitude)
    return point


def clear_db():
    cursor = connection.cursor()
    tables = ("advisers_location", "advisers_organisationtype", "advisers_outreachtype", "advisers_category")
    for table in tables:
        cursor.execute("TRUNCATE {table} RESTART IDENTITY CASCADE".format(table=table))


class UploadException(Exception):
    pass


class StrippedDict(dict):
    """
    A dict with all values stripped of leading and trailing whitespace on
    initializing
    """

    def __init__(self, iterable=None, **kwargs):
        iterable = ((k, v.strip() if isinstance(v, basestring) else v) for k, v in iterable)
        super(StrippedDict, self).__init__(iterable, **kwargs)


class GeocoderTask(Task):
    name = "advisers.tasks.GeocoderTask"

    def __init__(self):
        self.errors = []

    def run(self, *args, **kwargs):
        try:
            self.task_run_handler(*args, **kwargs)
        # This is raised when we abort the celery task with signal=SIGUSR1
        # See advisers.management.commands.utils.AbortImportMixin.cleanup_celery
        except SoftTimeLimitExceeded:
            raise Ignore()

    def task_run_handler(self, location_details):
        tot = len(location_details)

        def log_error(err):
            logging.warn(err)
            self.errors.append(err)

        for n, location in enumerate(location_details):
            postcode = re.sub(" +", " ", location["postcode"])

            outreach_type = "OFFICE LOCATION" if location["outreach_type"] is None else "OUTREACH SERVICE"

            org_name = location["org_name"]

            account_number = location["account_number"]

            firm = location["firm"]

            message_parts = []

            if outreach_type == "OFFICE LOCATION":
                message_parts.append(
                    f"; With the organisation name: {org_name}; The account number: {account_number}; And firm ID: {firm}."
                )

            try:
                point = geocode(postcode)
            except geocoder.PostcodeNotFound:
                log_error(
                    f"Failed geocoding postcode: {postcode}; On worksheet tab: {outreach_type}"
                    f"{''.join(message_parts)}"
                )
                continue
            except geocoder.GeocoderError as e:
                log_error(f"Failed postcode: {postcode}. Error connecting to geocoder: {e}")
                continue

            if point:
                locations = models.Location.objects.filter(postcode=postcode)
                locations.update(point=point)
                self.update_state(state="RUNNING", meta={"count": n, "total": tot, "errors": self.errors})

        # clean up task errors
        self.errors = []


class ProgressiveAdviserImport(Task):
    name = "advisers.tasks.ProgressiveAdviserImport"

    worksheet_names = (
        "LOCAL ADVICE ORG",
        "OFFICE LOCATION",
        "CAT OF LAW CRIME",
        "CAT OF LAW CIVIL",
        "OUTREACH SERVICE",
    )

    def __init__(self):
        self.total = None
        self.record = None
        self.sheets = {}
        self.temp_dir = tempfile.mkdtemp()
        self.progress = {"task": "initialising"}

    def truncate_and_upload_data_tables_from_xlsx(self, xlsx_file, *args, **kwargs):
        csv_metadata = self.convert_excel_to_csv(xlsx_file)
        for csv_filename, headers, types in csv_metadata:
            self.load_csv_into_db(csv_filename, headers, types)

        try:
            with transaction.atomic():
                clear_db()
                self.translate_data()
        except ProgrammingError as error:
            logging.warn(error)
            raise UploadException(error)

        for meta in csv_metadata:
            self.drop_csv_table(meta[0])

    def run(self, *args, **kwargs):
        try:
            self.task_run_handler(*args, **kwargs)
        except SoftTimeLimitExceeded:
            raise Ignore()

    def task_run_handler(self, xlsx_file, record=None, *args, **kwargs):
        import_object = models.Import.objects.get(task_id=self.request.id)
        import_object.start()
        self.record = record
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT advisers_location.id, postcode, advisers_organisation.name, advisers_organisation.firm, advisers_outreachtype.name, advisers_office.account_number
            FROM advisers_location
            LEFT JOIN advisers_office
            ON advisers_office.location_id = advisers_location.id
            LEFT JOIN advisers_organisation
            ON advisers_office.organisation_id = advisers_organisation.id
            LEFT JOIN advisers_outreachservice
            ON advisers_location.id = advisers_outreachservice.location_id
            LEFT JOIN advisers_outreachtype
            ON advisers_outreachtype.id = advisers_outreachservice.type_id
            """
        )
        results = cursor.fetchall()

        location_details = [
            {
                "id": location[0],
                "postcode": location[1],
                "org_name": location[2],
                "firm": location[3],
                "outreach_type": location[4],
                "account_number": location[5],
            }
            for location in results
        ]

        self.total = len(location_details)

        def chunks(n=1000):
            for i in xrange(0, len(location_details), n):
                yield location_details[i : i + n]

        self.update_count()

        tasks = []
        for chunk in chunks():
            t = GeocoderTask().subtask(args=(chunk,))
            tasks.append(t)
        ts = group(tasks)
        res = ts()

        task_counts = {}
        task_errors = {}

        def update_task_process(task_id, result):
            task_counts[task_id] = result.get("count")
            task_errors[task_id] = result.get("errors")

        while res.completed_count() < len(tasks):
            [update_task_process(r.task_id, r.result) for r in res if r.result]

            count = sum(task_counts.values())
            errors = list(itertools.chain(*task_errors.values()))
            self.update_count(count, errors)
            time.sleep(1)

        cache.clear()

    def update_count(self, count=0, errors=[], task="geocoding locations"):
        self.progress = {"task": task, "count": count, "total": self.total, "errors": errors}

        self.update_state(state="RUNNING", meta=self.progress)

    def on_success(self, retval, task_id, args, kwargs):
        import_object = models.Import.objects.get(task_id=self.request.id)
        import_object.complete()
        self.update_state(state=models.IMPORT_STATUSES.SUCCESS.upper(), meta=self.progress)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        import_object = models.Import.objects.get(task_id=self.request.id)
        import_object.status = models.IMPORT_STATUSES.FAILURE
        import_object.save()
        self.update_state(state=models.IMPORT_STATUSES.FAILURE.upper(), meta=self.progress)

    def convert_excel_to_csv(self, xlsx_file):
        workbook = xlrd.open_workbook(xlsx_file)
        csv_metadata = []
        for name in workbook.sheet_names():
            if name in self.worksheet_names:
                worksheet = workbook.sheet_by_name(name)
                csv_metadata.append(self.write_to_csv(name, worksheet))
        os.remove(xlsx_file)
        return csv_metadata

    def write_to_csv(self, name, worksheet):
        csv_filename = "{0}.csv".format(slugify(unicode(name)))
        csv_filename = os.path.join(self.temp_dir, csv_filename)
        headers = [unicode(value) for value in worksheet.row_values(0)]
        types = worksheet.row_types(1)

        def value(cell):
            if cell.ctype == xlrd.XL_CELL_NUMBER:
                return int(cell.value)
            return cell.value

        with open(csv_filename, "w") as csv_file:
            writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            for row in xrange(worksheet.nrows):
                items = [value(cell) for cell in worksheet.row(row)]
                writer.writerow(items)
        return csv_filename, headers, types

    def load_csv_into_db(self, csv_filename, headers, types):
        table_name = os.path.basename(csv_filename)[:-4].replace("-", "_")
        columns = [
            "{header} {ctype}".format(
                header=slugify(header).replace("-", "_"),
                ctype="integer" if type_ == xlrd.XL_CELL_NUMBER else "varchar",
            )
            for header, type_ in zip(headers, types)
        ]
        cursor = connection.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS {table} ({columns})".format(table=table_name, columns=", ".join(columns))
        )
        cursor.execute("DELETE FROM {table}".format(table=table_name))

        psql_command = [
            "export PGPASSWORD=%s &&" % settings.DATABASES["default"]["PASSWORD"],
            "psql",
            settings.DATABASES["default"]["NAME"],
            "-U",
            settings.DATABASES["default"]["USER"],
            "-h",
            settings.DATABASES["default"]["HOST"],
            "-c",
            "\"\\copy {table} FROM {filename} DELIMITER ',' CSV HEADER;\"".format(
                table=table_name, filename=csv_filename
            ),  # noqa: W605
        ]

        os.system(" ".join(psql_command))

    def drop_csv_table(self, csv_filename):
        table_name = os.path.basename(csv_filename)[:-4].replace("-", "_")
        cursor = connection.cursor()
        cursor.execute("DROP TABLE {table}".format(table=table_name))

    def translate_data(self):
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT
                INTO advisers_category (code, civil)
                SELECT DISTINCT
                    civil_category_code, true
                    FROM cat_of_law_civil"""
        )
        cursor.execute(
            """
            INSERT
                INTO advisers_category (code, civil)
                SELECT DISTINCT
                    crime_category_code, false
                    FROM cat_of_law_crime"""
        )
        cursor.execute(
            """
            INSERT
                INTO advisers_organisationtype (name)
                SELECT
                    DISTINCT(type_of_organisation)
                    FROM local_advice_org"""
        )

        cursor.execute(
            """
            INSERT
                INTO advisers_outreachtype (name)
                SELECT DISTINCT
                    pt_or_outreach_indicator
                    FROM outreach_service"""
        )

        cursor.execute("DROP FUNCTION IF EXISTS count_office_relations(integer);")

        cursor.execute(
            """
            CREATE OR REPLACE FUNCTION count_office_relations(
                _id int
                , OUT _count int)
                RETURNS int AS
                    $func$

                BEGIN

                SELECT INTO _count COUNT(*) FROM advisers_office o WHERE o.location_id=_id;

                RAISE NOTICE 'Location: % , Count: %', _id, _count;

                END
                $func$  LANGUAGE plpgsql"""
        )

        cursor.execute("DROP FUNCTION IF EXISTS count_outreachservice_relations(integer);")

        cursor.execute(
            """
            CREATE OR REPLACE FUNCTION count_outreachservice_relations(
                _id int
                , OUT _count int)
                RETURNS int AS
                    $func$

                BEGIN

                SELECT INTO _count COUNT(*) FROM advisers_outreachservice o WHERE o.location_id=_id;

                END
                $func$  LANGUAGE plpgsql"""
        )

        cursor.execute("DROP FUNCTION IF EXISTS fetch_free_location(integer);")

        cursor.execute(
            """
            CREATE OR REPLACE FUNCTION fetch_free_location(
                _address_line_1 character varying
                , _address_line_2 character varying
                , _address_line_3 character varying
                , _city character varying
                , _postcode character varying
                , OUT _id int)
                RETURNS int AS
                    $func$

                BEGIN

                SELECT INTO _id DISTINCT l.id
                    FROM advisers_location l
                    WHERE l.address = rtrim(
                                concat_ws(E'\\n',
                                    _address_line_1, _address_line_2,
                                    _address_line_3),
                                E'\\n ') AND
                            l.city = _city AND
                            l.postcode = _postcode AND
                          count_office_relations(l.id)=0 AND
                          count_outreachservice_relations(l.id)=0
                    ORDER BY l.id DESC
                    LIMIT 1;

                END
                $func$  LANGUAGE plpgsql"""
        )

        cursor.execute("DROP FUNCTION IF EXISTS load_offices(integer);")

        cursor.execute(
            """
            CREATE OR REPLACE FUNCTION load_offices()
                RETURNS void AS
                    $func$

                DECLARE
                    ol_row record;

                BEGIN

                    FOR ol_row IN
                        SELECT DISTINCT
                            ol.*, org.id as organisation_id
                        FROM office_location ol
                        JOIN advisers_organisation org ON org.firm = ol.firm_number
                    LOOP
                        INSERT INTO advisers_office (
                            telephone, account_number, location_id, organisation_id)
                        values(
                            ol_row.telephone_number,
                            ol_row.account_number,
                            fetch_free_location(ol_row.address_line_1, ol_row.address_line_2, ol_row.address_line_3, ol_row.city, ol_row.postcode),
                            ol_row.organisation_id );
                    END LOOP;

                END
                $func$  LANGUAGE plpgsql"""
        )

        cursor.execute("DROP FUNCTION IF EXISTS load_outreachservices(integer);")

        cursor.execute(
            """
            CREATE OR REPLACE FUNCTION load_outreachservices()
                RETURNS void AS
                    $func$

                DECLARE
                    os_row record;

                BEGIN

                    FOR os_row IN
                        SELECT DISTINCT
                            os.*, otype.id as type_id, office.id as office_id, cat.id as cat_id
                        FROM outreach_service os
                        JOIN advisers_outreachtype otype
                            ON otype.name = os.pt_or_outreach_indicator
                        JOIN advisers_office office
                            ON office.account_number = os.account_number
                        LEFT JOIN advisers_category cat
                            ON cat.code = os.category_of_law
                    LOOP
                        WITH aos as (
                            INSERT INTO advisers_outreachservice (
                                type_id, location_id, office_id)
                            values(
                                os_row.type_id,
                                fetch_free_location(os_row.pt_or_outreach_loc_address_line1, os_row.pt_or_outreach_loc_address_line2, os_row.pt_or_outreach_loc_address_line3, os_row.city_outreach, os_row.pt_or_outreach_loc_postcode),
                                os_row.office_id ) RETURNING id, os_row.cat_id as cat_id
                        ) INSERT INTO advisers_outreachservice_categories (
                            outreachservice_id, category_id)
                                SELECT id, cat_id FROM aos;
                    END LOOP;

                END
                $func$  LANGUAGE plpgsql"""
        )

        cursor.execute(
            """
            INSERT
                INTO advisers_organisation (
                    name, website, contracted, type_id, firm)
                SELECT
                    firm_name,
                    website,
                    (upper(la_contracted_status) = 'YES'),
                    (SELECT
                        id
                        FROM advisers_organisationtype orgtype
                        WHERE orgtype.name LIKE type_of_organisation),
                    firm_number
                    FROM local_advice_org"""
        )

        cursor.execute(
            """
            INSERT
                INTO advisers_location (address, city, postcode)
                SELECT
                    rtrim(
                        concat_ws(E'\\n',
                            address_line_1,
                            address_line_2,
                            address_line_3),
                        E'\\n '),
                    city,
                    postcode
                    FROM office_location"""
        )

        cursor.execute(
            """
            INSERT
                INTO advisers_location (address, city, postcode)
                SELECT
                    rtrim(
                        concat_ws(E'\\n',
                            pt_or_outreach_loc_address_line1,
                            pt_or_outreach_loc_address_line2,
                            pt_or_outreach_loc_address_line3),
                        E'\\n '),
                    city_outreach,
                    pt_or_outreach_loc_postcode
                    FROM outreach_service"""
        )

        cursor.execute("""SELECT * FROM load_offices()""")

        cursor.execute("""SELECT * FROM load_outreachservices()""")

        cursor.execute(
            """
            INSERT
                INTO advisers_office_categories (office_id, category_id)
                SELECT DISTINCT
                    off.id,
                    cat.id
                    FROM
                        cat_of_law_civil civ,
                        advisers_office off,
                        advisers_category cat,
                        advisers_organisation org
                    WHERE
                        org.firm = civ.firm_number AND
                        off.organisation_id = org.id AND
                        off.account_number = civ.account_number AND
                        cat.code = civ.civil_category_code"""
        )
        cursor.execute(
            """
            INSERT
                INTO advisers_office_categories (office_id, category_id)
                SELECT DISTINCT
                    off.id,
                    cat.id
                    FROM
                        cat_of_law_crime cri,
                        advisers_office off,
                        advisers_category cat,
                        advisers_organisation org
                    WHERE
                        org.firm = cri.firm_number AND
                        off.organisation_id = org.id AND
                        off.account_number = cri.account_number AND
                        cat.code = cri.crime_category_code"""
        )


app.register_task(GeocoderTask())
app.register_task(ProgressiveAdviserImport())
