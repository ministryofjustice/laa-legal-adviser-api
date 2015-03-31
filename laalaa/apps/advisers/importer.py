# -*- coding: utf-8 -*-
import logging
from threading import Thread
from time import sleep

from django.contrib.gis.geos import Point
from django.db import IntegrityError
import xlrd

from . import models
from . import geocoder


logging.basicConfig(filename='adviser_import.log', level=logging.WARNING)


cache = {}


def cached(fn):
    cache[fn.__name__] = {}

    def wrapped(name):
        if name not in cache[fn.__name__]:
            cache[fn.__name__][name] = fn(name)
        return cache[fn.__name__][name]
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
            if result['point']:
                point = Point(*result['point']['coordinates'])
    except geocoder.PostcodeNotFound:
        logging.warn('Failed geocoding postcode: %s' % postcode)
    except geocoder.GeocoderError as e:
        logging.warn('Error connecting to geocoder: %s' % e)
    return point


def join(*args):
    return '|'.join(args)


def location(address):
    addr1, addr2, addr3, city, pcode = address.split('|')
    address = '\n'.join(filter(None, [addr1, addr2, addr3]))
    loc = models.Location.objects.filter(
        address=address,
        city=city,
        postcode=pcode)
    if len(loc):
        return loc[0]
    location, created = models.Location.objects.get_or_create(
        address=address,
        city=city,
        postcode=pcode,
        point=geocode(pcode))
    return location


class ImportProcess(Thread):
    """
    Loads/Updates data from xsl spreadsheet
    """

    def __init__(self, path):
        self.progress = {
            'task': 'initializing',
            'count': 0,
            'total': 0}
        super(ImportProcess, self).__init__()
        workbook = xlrd.open_workbook(path)
        self.organisation_sheet = workbook.sheet_by_name('LOCAL ADVICE ORG')
        self.office_sheet = workbook.sheet_by_name('OFFICE LOCATION')
        self.category_criminal_sheet = workbook.sheet_by_name(
            'CAT OF LAW CRIME')
        self.category_civil_sheet = workbook.sheet_by_name('CAT OF LAW CIVIL')
        self.outreach_sheet = workbook.sheet_by_name('OUTREACH SERVICE')

    def sheet_to_dict(self, worksheet):
        """
        Parse worksheet into list of dicts
        """

        headings = [cell.value for cell in worksheet.row(0)]

        def value(cell):
            if cell.ctype == xlrd.XL_CELL_NUMBER:
                return int(cell.value)
            return cell.value.encode('utf-8', errors='ignore')

        def row(index):
            return dict(zip(headings, map(value, worksheet.row(index))))

        return map(row, range(1, worksheet.nrows))

    def import_organisations(self):
        orgtypes = {}

        rows = self.sheet_to_dict(self.organisation_sheet)
        self.progress = {
            'task': 'Importing organisations',
            'total': len(rows),
            'count': 0}

        def orgtype(name):
            orgtype, created = models.OrganisationType.objects.get_or_create(
                name=name)
            return orgtype

        def org(data):
            _orgtype = orgtype(data['Type of Organisation'])
            try:
                org, created = models.Organisation.objects.get_or_create(
                    firm=data['Firm Number'],
                    name=data['Firm Name'],
                    website=data['Website'],
                    contracted=data['LA Contracted Status'],
                    type_id=_orgtype.id)
            except IntegrityError:
                print data, _orgtype.id
                raise
            self.progress['count'] += 1

        map(org, rows)

    def import_offices(self):

        rows = self.sheet_to_dict(self.office_sheet)
        self.progress = {
            'task': 'Importing offices',
            'total': len(rows),
            'count': 0}

        def office(data):
            loc = location(join(
                data['Address Line 1'],
                data['Address Line 2'],
                data['Address Line 3'],
                data['City'],
                data['Postcode']))
            org = models.Organisation.objects.filter(firm=data['Firm Number'])
            office, created = models.Office.objects.get_or_create(
                telephone=data['Telephone Number'],
                account_number=data['Account Number'].upper(),
                organisation_id=org[0].id,
                location=loc)
            self.progress['count'] += 1

        map(office, rows)

    def import_outreach(self):
        outreachtypes = {}

        rows = self.sheet_to_dict(self.outreach_sheet)
        self.progress = {
            'task': 'Importing outreach locations',
            'total': len(rows),
            'count': 0}

        @cached
        def outreachtype(name):
            outreachtype, created = models.OutreachType.objects.get_or_create(
                name=name)
            return outreachtype

        def outreach(data):
            loc = location(join(
                data['PT or Outreach Loc Address Line1'],
                data['PT or Outreach Loc Address Line2'],
                data['PT or Outreach Loc Address Line3'],
                data['City (outreach)'],
                data['PT or Outreach Loc Postcode']))
            offices = models.Office.objects.filter(
                account_number=data['Account Number'].upper())
            office = None
            if len(offices):
                office = offices[0]
            _outreachtype = outreachtype(data['PT or Outreach Indicator'])
            outreach, created = models.OutreachService.objects.get_or_create(
                type_id=_outreachtype.id,
                location_id=loc.id,
                office_id=office.id)
            self.progress['count'] += 1

        map(outreach, rows)

    def run(self):
        self.import_organisations()
        self.import_offices()
        self.import_outreach()
        self.progress = {'task': 'done'}


class ImportShellRun(object):

    def __call__(self, path):
        importer = ImportProcess(path)
        importer.start()

        while importer.is_alive() and importer.progress['task'] is not None:
            sleep(1)
            print '{task}'.format(**importer.progress),
            if importer.progress['total']:
                print '\b: {count} / {total}'.format(**importer.progress)
            else:
                print ''
