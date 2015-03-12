# -*- coding: utf-8 -*-
import xlrd

from .models import Category, OrganisationType, Organisation, Location, Office, OutreachType, OutreachService


class AdviserImport(object):
    """
    Loads/Updates data from xsl spreadsheet
    """
    def __init__(self, path):
        workbook = xlrd.open_workbook(path)
        self.organisation_sheet = workbook.sheet_by_name('LOCAL ADVISE ORG')
        self.office_sheet = workbook.sheet_by_name('OFFICE LOCATION')
        self.category_criminal_sheet = workbook.sheet_by_name('CAT OF LAW CRIME')
        self.category_civil_sheet = workbook.sheet_by_name('CAT OF LAW CIVIL')
        self.outreach_sheet = workbook.sheet_by_name('OUTREACH SERVICE')

    def sheet_to_dict(self, worksheet):
        data = []
        header = [h.value for h in worksheet.row(0)]
        for curr_row in range(1, worksheet.nrows):
            row = [int(each.value)
                   if isinstance(each.value, float)
                   else each.value
                   for each in worksheet.row(curr_row)]
            value_dict = dict(zip(header, row))

            data.append(value_dict)

        return data