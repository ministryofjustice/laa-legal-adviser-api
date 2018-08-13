from django.test import TestCase

import mock
import advisers.pc_fallback
import advisers.geocoder


class FallbackTest(TestCase):

    def setUp(self):
        self.postcode = 'sw1a1aa'
        pass

    @mock.patch('postcodes.PostCoder.get')
    def test_fallback_geocode_returns_none_if_lookup_fails(self, postcoder_get_mock):
        postcoder_get_mock.return_value = None
        self.assertIsNone(advisers.pc_fallback.geocode(self.postcode))

    @mock.patch('postcodes.PostCoder.get')
    def test_fallback_geocode_returns_a_postcode_placeholder_if_it_succeeds(self, postcoder_get_mock):
        fallback_postcode = {'postcode': 'SW1A 1AA', 'geo': {'lat': 51.501009, 'lng': -0.141588}}
        postcoder_get_mock.return_value = fallback_postcode

        result = advisers.pc_fallback.geocode(self.postcode)
        self.assertEquals(result.postcode, 'sw1a1aa')
        self.assertEquals(result.latitude, 51.501009)
        self.assertEquals(result.longitude, -0.141588)

    @mock.patch('postcodeinfo.Client.lookup_postcode')
    @mock.patch('postcodes.PostCoder.get')
    def test_postcodeinfo_geocode_failure_triggers_fallback_geocode(self, postcoder_get_mock, lookup_postcode_mock):
        fallback_postcode = {'postcode': 'SW1A 1AA', 'geo': {'lat': 51.501009, 'lng': -0.141588}}

        lookup_postcode_mock.return_value.valid = False
        postcoder_get_mock.return_value = fallback_postcode

        result = advisers.geocoder.geocode(self.postcode)
        self.assertEquals(result.postcode, 'sw1a1aa')
        self.assertEquals(result.latitude, 51.501009)
        self.assertEquals(result.longitude, -0.141588)
