# -*- coding: utf-8 -*-
import logging
from threading import Thread
from time import sleep

from django.contrib.gis.geos import Point
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
    point = Point(0.0, 0.0)
    try:
        result = geocoder.geocode(postcode)
        point = Point(*result['point']['coordinates'])
    except geocoder.PostcodeNotFound:
        logging.warn('Failed geocoding postcode: %s' % postcode)
    except geocoder.GeocoderError as e:
        logging.warn('Error connecting to geocoder: %s' % e)
    return point


def join(*args):
    return '|'.join(args)


@cached
def location(address):
    addr1, addr2, addr3, city, pcode = address.split('|')
    location = models.Location()
    location.address = '\n'.join(filter(None, [addr1, addr2, addr3]))
    location.city = city
    location.postcode = pcode
    postcode = pcode.replace(u' ', u'').lower()
    location.point = geocode(postcode)
    location.save()
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
        self.category_criminal_sheet = workbook.sheet_by_name('CAT OF LAW CRIME')
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
            return cell.value.decode('utf8')

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

        @cached
        def orgtype(name):
            orgtype = models.OrganisationType()
            orgtype.name = name
            orgtype.save()
            return orgtype

        def org(data):
            org = models.Organisation()
            org.id = data['Firm Number']
            org.name = data['Firm Name']
            org.website = data['Website']
            org.contracted = data['LA Contracted Status']
            org.type = orgtype(data['Type of Organisation'])
            org.save()
            self.progress['count'] += 1

        map(org, rows)

    def import_offices(self):

        rows = self.sheet_to_dict(self.office_sheet)
        self.progress = {
            'task': 'Importing offices',
            'total': len(rows),
            'count': 0}

        def office(data):
            office = models.Office()
            office.telephone = data['Telephone Number']
            office.account_number = data['Account Number'].upper()
            office.organisation_id = data['Firm Number']
            office.location = location(join(
                data['Address Line 1'],
                data['Address Line 2'],
                data['Address Line 3'],
                data['City'],
                data['Postcode']))
            office.save()
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
            outreachtype = models.OutreachType()
            outreachtype.name = name
            outreachtype.save()
            return outreachtype

        def outreach(data):
            outreach = models.OutreachService()
            outreach.type = outreachtype(data['PT or Outreach Indicator'])
            outreach.location = location(join(
                data['PT or Outreach Loc Address Line1'],
                data['PT or Outreach Loc Address Line2'],
                data['PT or Outreach Loc Address Line3'],
                data['City (outreach)'],
                data['PT or Outreach Loc Postcode']))
            try:
                outreach.office = models.Office.objects.get(
                    account_number=data['Account Number'].upper())
            except models.Office.DoesNotExist:
                print data['Account Number']
                raise
            outreach.save()
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
