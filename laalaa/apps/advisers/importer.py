# -*- coding: utf-8 -*-
import logging
import sys

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
        point = geocoder.geocode(postcode)
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
    postcode = pcode.encode('utf-8').replace(
        u' ', u'').replace(u'\xa0', u'').lower()
    location.point = geocode(postcode)
    location.save()
    sys.stdout.write('o')
    sys.stdout.flush()
    return location


def save(obj):
    obj.save()
    sys.stdout.write('.')
    sys.stdout.flush()


class AdviserImport(object):
    """
    Loads/Updates data from xsl spreadsheet
    """
    def __init__(self, path):
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
            if isinstance(cell.value, float):
                return int(cell.value)
            return cell.value

        def row(index):
            return dict(zip(headings, map(value, worksheet.row(index))))

        return map(row, range(1, worksheet.nrows))

    def import_organisations(self):
        orgtypes = {}

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
            return org

        orgs = map(org, self.sheet_to_dict(self.organisation_sheet))
        map(save, orgs)
        print '\nSaved %d organisations' % len(orgs)

    def import_offices(self):

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
            return office

        offices = map(office, self.sheet_to_dict(self.office_sheet))
        map(save, offices)
        print '\nSaved %d offices' % len(offices)

    def import_outreach(self):
        outreachtypes = {}

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
            return outreach

        outreach_locs = map(outreach, self.sheet_to_dict(self.outreach_sheet))
        map(save, outreach_locs)
        print '\nSaved %d outreach locations' % len(outreach_locs)

    def import_all(self):
        self.import_organisations()
        self.import_offices()
        self.import_outreach()
