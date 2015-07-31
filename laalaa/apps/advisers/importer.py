# -*- coding: utf-8 -*-
import logging
from threading import Thread, Event
from time import sleep

from django.contrib.gis.geos import Point
from django.db import IntegrityError
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
    print "Caching known postcode locations"
    for location_model in models.Location.objects.exclude(point__isnull=True):
        geocode.cache[location_model.postcode] = location_model.point


def location(address):
    addr1, addr2, addr3, city, pcode = address
    address = '\n'.join(filter(None, [addr1, addr2, addr3]))
    loc = models.Location.objects.filter(
        address=address,
        city=city,
        postcode=pcode)
    if loc.exists():
        if loc.first().point is None:
            point = geocode(pcode)
            if point is not None:
                # previously unknown postcode found
                loc.update(point=point)
        return loc.first()
    _location, _ = models.Location.objects.get_or_create(
        address=address,
        city=city,
        postcode=pcode,
        point=geocode(pcode))
    return _location


class ImportProcess(Thread):
    """
    Loads/Updates data from xls spreadsheet
    """

    def __init__(self, path, should_prime_geocoder=True):
        super(ImportProcess, self).__init__()
        self.progress = {'task': 'initialising'}
        self._interrupt = Event()
        self.should_prime_geocoder = should_prime_geocoder
        workbook = xlrd.open_workbook(path)
        self.organisation_sheet = workbook.sheet_by_name('LOCAL ADVICE ORG')
        self.office_sheet = workbook.sheet_by_name('OFFICE LOCATION')
        self.category_criminal_sheet = workbook.sheet_by_name(
            'CAT OF LAW CRIME')
        self.category_civil_sheet = workbook.sheet_by_name('CAT OF LAW CIVIL')
        self.outreach_sheet = workbook.sheet_by_name('OUTREACH SERVICE')

    def interrupt(self):
        self._interrupt.set()

    def check_interrupt(self):
        if self._interrupt.is_set():
            raise KeyboardInterrupt

    @classmethod
    def sheet_to_dict(cls, worksheet):
        """
        Parse worksheet into list of dicts
        """
        class StrippedDict(dict):
            def __init__(self, iterable=None, **kwargs):
                iterable = ((k, v.strip() if isinstance(v, basestring) else v) for k, v in iterable)
                super(StrippedDict, self).__init__(iterable, **kwargs)

        headings = [_cell.value for _cell in worksheet.row(0)]

        def value(cell):
            if cell.ctype == xlrd.XL_CELL_NUMBER:
                return int(cell.value)
            return cell.value.encode('utf-8', errors='ignore')

        def row(index):
            return StrippedDict(zip(headings, map(value, worksheet.row(index))))

        return map(row, range(1, worksheet.nrows))

    def import_organisations(self):

        rows = self.sheet_to_dict(self.organisation_sheet)
        self.progress = {
            'task': 'Importing organisations',
            'total': len(rows),
            'count': 0}

        def orgtype(name):
            _orgtype, _ = models.OrganisationType.objects.get_or_create(
                name=name)
            return _orgtype

        def org(data):
            self.check_interrupt()
            _orgtype = orgtype(data['Type of Organisation'])
            try:
                models.Organisation.objects.get_or_create(
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
            self.check_interrupt()
            loc = location((
                data['Address Line 1'],
                data['Address Line 2'],
                data['Address Line 3'],
                data['City'],
                data['Postcode']))
            org = models.Organisation.objects.filter(firm=data['Firm Number']).first()
            account_number = data['Account Number'].upper()
            try:
                _office = models.Office.objects.get(account_number=account_number)
                _office.telephone = data['Telephone Number']
                _office.organisation_id = org.id
                _office.location_id = loc.id
                _office.save()
            except models.Office.DoesNotExist:
                models.Office.objects.create(
                    telephone=data['Telephone Number'],
                    account_number=account_number,
                    organisation_id=org.id,
                    location_id=loc.id)
            self.progress['count'] += 1

        map(office, rows)

    def import_outreach(self):

        rows = self.sheet_to_dict(self.outreach_sheet)
        self.progress = {
            'task': 'Importing outreach locations',
            'total': len(rows),
            'count': 0}

        @cached
        def outreachtype(name):
            _outreachtype, _ = models.OutreachType.objects.get_or_create(
                name=name)
            return _outreachtype

        def outreach(data):
            self.check_interrupt()
            loc = location((
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
            models.OutreachService.objects.get_or_create(
                type_id=_outreachtype.id,
                location_id=loc.id,
                office_id=office.id)
            self.progress['count'] += 1

        map(outreach, rows)

    def import_categories(self):
        rows = self.sheet_to_dict(self.category_civil_sheet)
        self.progress = {
            'task': 'Importing civil categories',
            'total': len(rows),
            'count': 0}

        @cached
        def category(code_civil):
            code, civil = code_civil
            cat, _ = models.Category.objects.get_or_create(
                code=code,
                civil=civil)
            return cat

        @cached
        def office(firm_acct):
            firm_id, acct_no = firm_acct
            return models.Office.objects.get(
                organisation__firm=firm_id,
                account_number=acct_no.upper())

        def assoc_cat(data, civil=True):
            self.check_interrupt()
            key = 'Civil Category Code'
            if not civil:
                key = 'Crime Category Code'
            cat = category((data[key], civil))
            try:
                off = office((
                    data['Firm Number'],
                    data['Account Number']))
                off.categories.add(cat)
            except models.Office.DoesNotExist:
                logging.warn(
                    'Office for firm %s with acct no %s not found' %
                    (data['Firm Number'], data['Account Number']))
            self.progress['count'] += 1

        map(assoc_cat, rows)

        def assoc_criminal_cat(data):
            self.check_interrupt()
            assoc_cat(data, civil=False)

        rows = self.sheet_to_dict(self.category_criminal_sheet)
        self.progress = {
            'task': 'Importing criminal categories',
            'total': len(rows),
            'count': 0}

        map(assoc_criminal_cat, rows)

    def run(self):
        try:
            actions = [self.import_organisations, self.import_offices,
                       self.import_outreach, self.import_categories]
            if self.should_prime_geocoder:
                actions.insert(0, prime_geocoder_cache)
            for action in actions:
                self.check_interrupt()
                action()
            self.progress = {'task': 'done'}
        except KeyboardInterrupt:
            pass
        finally:
            # this helps geodjango in garbage collection
            geocode.clear_cache()


class ImportShellRun(object):

    def __call__(self, path, should_prime_geocoder=True):
        importer = ImportProcess(path, should_prime_geocoder=should_prime_geocoder)
        importer.start()

        try:
            while importer.is_alive() and importer.progress['task'] is not None:
                sleep(1)
                print '{task}'.format(**importer.progress),
                if 'total' in importer.progress:
                    print '\b: {count} / {total}'.format(**importer.progress)
                else:
                    print ''
        except KeyboardInterrupt:
            print "Interrupting importer thread"
            importer.interrupt()
            importer.join()
            print "Importer stopped"
