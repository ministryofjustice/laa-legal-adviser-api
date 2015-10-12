# -*- coding: utf-8 -*-
import csv
import logging
import os
import tempfile
from threading import Thread, Event
from time import sleep

from django.contrib.gis.geos import Point
from django.db import connection, transaction
from django.utils.text import slugify
import xlrd

from . import models
from . import geocoder


logging.basicConfig(filename='adviser_import.log', level=logging.WARNING)


def cached(fn):
    cache = {}

    def wrapped(name):
        if name not in cache:
            cache[name] = fn(name)
        return cache[name]

    wrapped.cache = cache
    wrapped.clear_cache = cache.clear
    return wrapped


@cached
def geocode(postcode):
    point = None
    try:
        loc = models.Location.objects.filter(postcode=postcode)
        if len(loc) and loc[0].point:
            point = loc[0].point
        else:
            result = geocoder.geocode(postcode)
            point = Point(result.longitude, result.latitude)
    except geocoder.PostcodeNotFound:
        logging.warn('Failed geocoding postcode: %s' % postcode)
    except geocoder.GeocoderError as e:
        logging.warn('Error connecting to geocoder: %s' % e)
    return point


def prime_geocoder_cache():
    """
    Cache known postcode locations
    """
    for location in models.Location.objects.exclude(point__isnull=True):
        geocode.cache[location.postcode] = location.point


def clear_db():
    cursor = connection.cursor()
    tables = (
        'advisers_location',
        'advisers_organisationtype',
        'advisers_outreachtype',
        'advisers_category')
    for table in tables:
        cursor.execute("TRUNCATE {table} RESTART IDENTITY CASCADE".format(
            table=table))


class StrippedDict(dict):
    """
    A dict with all values stripped of leading and trailing whitespace on
    initializing
    """

    def __init__(self, iterable=None, **kwargs):
        iterable = (
            (k, v.strip() if isinstance(v, basestring) else v)
            for k, v in iterable)
        super(StrippedDict, self).__init__(iterable, **kwargs)


class ImportProcess(Thread):
    """
    Loads/Updates data from xls spreadsheet
    """

    worksheet_names = (
        'LOCAL ADVICE ORG',
        'OFFICE LOCATION',
        'CAT OF LAW CRIME',
        'CAT OF LAW CIVIL',
        'OUTREACH SERVICE',
    )

    def __init__(self, xlsx_file, record, **options):
        super(ImportProcess, self).__init__()
        self.options = options
        self.progress = {'task': 'initialising'}
        self.record = record
        self._interrupt = Event()
        self.sheets = {}
        self.temp_dir = tempfile.mkdtemp()

        if options.pop('single_transaction', True):
            self.run = transaction.atomic(self.run)

        if options.pop('prime_geocoder', True):
            prime_geocoder_cache()

        if options.pop('clear_db', True):
            clear_db()

        csv_metadata = self.convert_excel_to_csv(xlsx_file)
        for csv_filename, headers, types in csv_metadata:
            self.load_csv_into_db(csv_filename, headers, types)

        self.translate_data()

        for meta in csv_metadata:
            self.drop_csv_table(meta[0])

    def convert_excel_to_csv(self, xlsx_file):
        workbook = xlrd.open_workbook(xlsx_file)
        csv_metadata = []
        for name in workbook.sheet_names():
            if name in self.worksheet_names:
                worksheet = workbook.sheet_by_name(name)
                csv_metadata.append(self.write_to_csv(name, worksheet))
        return csv_metadata

    def write_to_csv(self, name, worksheet):
        csv_filename = '{0}.csv'.format(slugify(unicode(name)))
        csv_filename = os.path.join(self.temp_dir, csv_filename)
        headers = [unicode(value) for value in worksheet.row_values(0)]
        types = worksheet.row_types(1)

        def value(cell):
            if cell.ctype == xlrd.XL_CELL_NUMBER:
                return int(cell.value)
            return cell.value.encode('utf-8', errors='ignore')

        with open(csv_filename, 'wb') as csv_file:
            writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            for row in xrange(worksheet.nrows):
                writer.writerow([
                    value(cell)
                    for cell in worksheet.row(row)])
        return csv_filename, headers, types

    def load_csv_into_db(self, csv_filename, headers, types):
        table_name = os.path.basename(csv_filename)[:-4].replace('-', '_')
        columns = [
            '{header} {ctype}'.format(
                header=slugify(header).replace('-', '_'),
                ctype='integer' if type_ == xlrd.XL_CELL_NUMBER else 'varchar')
            for header, type_ in zip(headers, types)]
        cursor = connection.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS {table} ({columns})".format(
                table=table_name,
                columns=', '.join(columns)))
        cursor.execute("DELETE FROM {table}".format(table=table_name))
        cursor.execute(
            "COPY {table} FROM '{filename}' DELIMITER ',' CSV HEADER".format(
                table=table_name,
                filename=csv_filename))

    def drop_csv_table(self, csv_filename):
        table_name = os.path.basename(csv_filename)[:-4].replace('-', '_')
        cursor = connection.cursor()
        cursor.execute("DROP TABLE {table}".format(table=table_name))

    def translate_data(self):
        cursor = connection.cursor()
        cursor.execute("""
            INSERT
                INTO advisers_organisationtype (name)
                SELECT
                    DISTINCT(type_of_organisation)
                    FROM local_advice_org""")
        cursor.execute("""
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
                    FROM local_advice_org""")

        cursor.execute("""
            INSERT
                INTO advisers_location (address, city, postcode)
                SELECT DISTINCT
                    rtrim(
                        concat_ws(E'\\n',
                            address_line_1,
                            address_line_2,
                            address_line_3),
                        E'\\n '),
                    city,
                    postcode
                    FROM office_location""")

        cursor.execute("""
            INSERT
                INTO advisers_office (
                    telephone, account_number, location_id, organisation_id)
                SELECT
                    telephone_number,
                    account_number,
                    loc.id as location_id,
                    org.id as organisation_id
                    FROM office_location office
                    JOIN advisers_location loc
                        ON loc.address = rtrim(
                                concat_ws(E'\\n',
                                    address_line_1, address_line_2,
                                    address_line_3),
                                E'\\n ') AND
                            loc.city = office.city AND
                            loc.postcode = office.postcode
                    JOIN advisers_organisation org
                        ON org.firm = firm_number""")

        cursor.execute("""
            INSERT
                INTO advisers_outreachtype (name)
                SELECT DISTINCT
                    pt_or_outreach_indicator
                    FROM outreach_service""")

        cursor.execute("""
            INSERT
                INTO advisers_location (address, city, postcode)
                SELECT DISTINCT
                    rtrim(
                        concat_ws(E'\\n',
                            pt_or_outreach_loc_address_line1,
                            pt_or_outreach_loc_address_line2,
                            pt_or_outreach_loc_address_line3),
                        E'\\n '),
                    city_outreach,
                    pt_or_outreach_loc_postcode
                    FROM outreach_service
                    EXCEPT
                        SELECT
                            address, city, postcode
                            FROM advisers_location""")

        cursor.execute("""
            INSERT
                INTO advisers_outreachservice (
                    type_id, location_id, office_id)
                SELECT
                    otype.id as type_id,
                    loc.id as location_id,
                    office.id as office_id
                    FROM outreach_service os
                    JOIN advisers_outreachtype otype
                        ON otype.name = os.pt_or_outreach_indicator
                    JOIN advisers_location loc
                        ON loc.address = rtrim(
                            concat_ws(E'\\n',
                                os.pt_or_outreach_loc_address_line1,
                                os.pt_or_outreach_loc_address_line2,
                                os.pt_or_outreach_loc_address_line3),
                            E'\\n ') AND
                        loc.city = os.city_outreach AND
                        loc.postcode = os.pt_or_outreach_loc_postcode
                    JOIN advisers_office office
                        ON office.account_number = os.account_number""")

        cursor.execute("""
            INSERT
                INTO advisers_category (code, civil)
                SELECT DISTINCT
                    civil_category_code, true
                    FROM cat_of_law_civil""")
        cursor.execute("""
            INSERT
                INTO advisers_category (code, civil)
                SELECT DISTINCT
                    crime_category_code, false
                    FROM cat_of_law_crime""")
        cursor.execute("""
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
                        cat.code = civ.civil_category_code""")
        cursor.execute("""
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
                        cat.code = cri.crime_category_code""")

    def interrupt(self):
        self._interrupt.set()

    def check_interrupt(self):
        if self._interrupt.is_set():
            raise KeyboardInterrupt

    def increment_progress(self, num):
        self.progress['count'] += num

    def run(self):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT DISTINCT postcode FROM advisers_location""")
        postcodes = cursor.fetchall()

        def chunks(n=1000):
            for i in xrange(0, len(postcodes), n):
                yield postcodes[i:i + n]

        self.progress = {
            'task': 'geocoding locations',
            'count': 0,
            'total': len(postcodes)}

        threads = []
        for i, chunk in enumerate(chunks()):
            thread = GeocoderThread(i, chunk, self)
            thread.start()
            threads.append(thread)

        try:
            while any(map(lambda x: x.is_alive(), threads)):
                self.check_interrupt()
                sleep(1)

        except KeyboardInterrupt:
            for i, thread in enumerate(threads):
                print 'Stopping geocoder thread %d' % i
                thread.interrupt()
                thread.join()
            self.record.status = models.IMPORT_STATUSES.ABORTED

        except Exception:
            self.record.status = models.IMPORT_STATUSES.FAILURE
            raise

        else:
            self.record.status = models.IMPORT_STATUSES.SUCCESS

        finally:
            # this helps geodjango in garbage collection
            geocode.clear_cache()
            self.record.save()


class GeocoderThread(Thread):

    def __init__(self, num, postcodes, importer, *args, **kwargs):
        super(GeocoderThread, self).__init__(*args, **kwargs)
        self._interrupt = Event()
        self.num = num
        self.postcodes = postcodes
        self.importer = importer

    def run(self):
        try:
            for postcode in self.postcodes:
                self.check_interrupt()
                point = geocode(postcode[0].encode('utf-8'))
                if point:
                    models.Location.objects.filter(
                        postcode=postcode[0]
                    ).update(point=point)
                    self.importer.increment_progress(1)

        except KeyboardInterrupt:
            pass

    def interrupt(self):
        self._interrupt.set()

    def check_interrupt(self):
        if self._interrupt.is_set():
            raise KeyboardInterrupt


def import_running():
    return 0 < models.Import.objects.filter(
        status__in=models.IMPORT_STATUSES.RUNNING).count()


class Import(object):

    class ImportError(Exception):
        pass

    class Balk(ImportError):
        pass

    class Fail(ImportError):
        pass

    def __init__(self, xlsx_file, user=None, **options):
        self.xlsx_file = xlsx_file
        self.user = user
        self.options = options
        self.record = None
        self.thread = None

    def start(self):
        if import_running():
            raise Import.Balk()

        record = models.Import.objects.create(
            status=models.IMPORT_STATUSES.RUNNING,
            filename=self.xlsx_file,
            user=self.user)

        try:
            self.thread = ImportProcess(self.xlsx_file, record, **self.options)

        except xlrd.XLRDError as error:
            raise Import.Fail(error)

        self.thread.start()

    @property
    def task(self):
        if self.thread:
            return self.thread.progress.get('task')

    @property
    def count(self):
        if self.thread:
            return self.thread.progress.get('count')

    @property
    def total(self):
        if self.thread:
            return self.thread.progress.get('total')

    def is_running(self):
        return (
            self.thread and
            self.thread.is_alive() and
            self.thread.progress.get('task') is not None)

    @property
    def progress(self):
        return '{task}{progress}'.format(
            task=self.task,
            progress=(
                ': {0.count} / {0.total}'.format(self)
                if self.total else ''))

    def stop(self):
        if self.is_running():
            self.thread.interrupt()
            self.thread.join()
