# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from .. import geocoder


FAILING_POSTCODES = [
    'LE1 5BU',
    'W1J 6BD',
    'CF11 5EQ',
    'EN8 9XB',
    'WA10 1QW',
    'LE15 6QH',
    'EC2N 2BR',
    'ST6 1AW',
    'UB4 0PU',
    'B93 ODX',
    'KT1 2PS',
    'TA1 1RL',
    'PE29 3TD',
    'NW6 2DD',
    'W1T 6AF',
    'L2 5JE',
    'SW1V 1EH',
    'WD17 1DR',
    'SE1 7UJ',
    'NP13 1YB',
    'PO9 1UL',
    'LS1 3BG',
    'BL9 0DX',
    'CM20 1ND',
    'PO9 1PA',
    'WA7 2HF',
    'CH41 5JF',
    'RG1 1SH',
    'DA12 1BQ',
    'LN1 1UW',
    'CF11 9LU',
    'NP16 3EF',
    'BD21 3AG',
    'PE21 6QL',
    'B3 3SH',
    'SO15 2UT',
    'CT9 2QT',
    'NN10 0PT',
    'BH14 9DY',
    'ME14 1JE',
    'RH11 7AF',
    'LN2 1DA',
    'WD24 4AQ',
    'N1 1RY',
    'LS2 8BA',
    'L2 0XG',
    'LN5 7PS',
    'BS1 4LY',
    'BB2 6AS',
    'N3 1LQ',
    'AL5 2SW',
    'SA15 3AL',
    'HU1 2AD',
    'BD21 3DT',
    'RG41 3AT',
    'NE63 8RL',
    'S65 1AA',
    'OX1 1TL',
    'YO8 4PX',
    'NE6 2HL',
    'YO1 6HP',
    'SO1 2XQ',
    'CH65 0HW',
    'N1 8UY',
    'SP2 7WP',
    'NN4 7SH',
    'LS12 6LN',
    'OL13 9AN',
    'SE5 0HF',
    'OL6 6DL',
    'WN1 1NG',
    'IP4 1NF',
    'L2 0NB',
    'TR1 2EY',
    'CA28 7NR',
    'ME4 4LY',
    'CH7 1BJ',
    'N7 9PD',
    'HD1 1QB',
    'BS1 5TR',
    'L2 2BX',
    'S80 1JE',
    'SE13 5LA',
    'LL65 1UR',
    'RM1 3LT',
    'SN1 2HG',
    'IG1 1TP',
    'TQ6 9PT',
    'ST1 1HQ',
    'N1 6PA',
    'SS17 7JL',
    'NR30 2JP',
    'SS1 1BB',
    'E15 4BX',
    'WS13 6LW',
    'M60 0AG',
    'MK9 2UB',
    'CR9 2ER',
    'WD17 1ST',
    'NN8 4JW',
    'SA13 1HX',
    'WV7 3HA',
    'SL6 8BE',
    'L11 8PN',
    'SG1 1AF',
    'W1A 3AE',
    'TF11 1JP',
    'CF47 8BU',
    'L11 1JS',
    'SL11 8NX',
    'SG7 6BD',
    'LL30 2T',
    'DN1 2DP',
    'EC4N 7DZ',
    'RH5 6BX',
    'HA1 1EJ',
    'KT1 2AD',
    'W14 8TH',
    'NW5 1RS',
    'SA11 3LP',
    'HA0 3NF',
    'SA11 1LF',
    'EC2V 7AW',
    'WC2E 8HA',
    'DE14 1BP',
    'DL14 6FE',
    'CR9 3NG',
    'DN14 5AE',
    'B11 1HP',
    'NR32 1PG',
    'NG1 7EJ',
    'ME7 4NX',
    'SW1H 0RG',
    'BS1 6BB',
    'W14 0GL',
    'TR1 3FF',
    'PO19 1TH',
    'EX8 1HQ',
    'CT6 6LE',
    'DY1 1RY',
    'BB8 0BX',
    'CB2 1BY',
    'NR30 2QJ',
    'JE2 3WP',
    'MK9 2LJ',
    'HU1 3DZ',
    'SM1 4JH',
]


class GeocodeTestCase(TestCase):
    def test_failing_postcodes(self):
        passed = []
        failed = []
        for pc in FAILING_POSTCODES:
            try:
                point = geocoder.geocode(pc)
                passed.append(pc)
            except geocoder.PostcodeNotFound:
                failed.append(pc)
            except geocoder.GeocoderError as e:
                failed.append(pc)

        if failed:
            self.fail('failed to geocode %s of %s' % (len(failed),
                                                      len(FAILING_POSTCODES)))