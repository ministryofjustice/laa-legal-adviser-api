import json
import mock
import unittest
import django.test
import requests

from rest_framework.test import APIRequestFactory
from advisers import geocoder
from advisers.views import AdviserViewSet
from advisers import pc_fallback


class GeocoderTest(unittest.TestCase):

    def setUp(self):
        self.postcode = 'sw1a1aa'
        self.good_result = u'{"status":200,"result":{"postcode":"SW1A 1AA","longitude":-0.141588,"latitude":51.501009}}'

    @mock.patch('lib.PostCodeClient.getLookupPostCode')
    def test_geocode_calls_postcode_lookup(self, lookup_mock):
        lookup_mock.return_value = self.good_result
        result = geocoder.geocode(self.postcode)

        self.assertEqual(result.postcode, 'sw1a1aa')
        self.assertEqual(result.latitude, 51.501009)
        self.assertEqual(result.longitude, -0.141588)


    @mock.patch('lib.PostCodeClient.getLookupPostCode')
    def test_raises_geocoder_error_when_postcode_lookup_fails_with_timeout(self, lookup_mock):
        lookup_mock.side_effect = requests.exceptions.ConnectTimeout()

        with self.assertRaisesRegexp(geocoder.GeocoderError, 'Caused by ConnectTimeout'):
            geocoder.geocode(self.postcode)


    @mock.patch('lib.PostCodeClient.getLookupPostCode')
    def test_raises_geocoder_error_when_postcode_lookup_fails_with_server_error(self, lookup_mock):
        lookup_mock.return_value = u'{"status":500,"message":"Bad things happened"}'

        with self.assertRaisesRegexp(geocoder.GeocoderError, 'Bad things happened'):
            geocoder.geocode(self.postcode)


    @mock.patch('lib.PostCodeClient.getLookupPostCode')
    def test_raises_geocoder_error_when_postcode_lookup_fails_with_client_error(self, lookup_mock):
        lookup_mock.return_value = u'{"status":400,"message":"Invalid request"}'

        with self.assertRaisesRegexp(geocoder.GeocoderError, 'Invalid request'):
            geocoder.geocode(self.postcode)


    @mock.patch('lib.PostCodeClient.getLookupPostCode')
    def test_raises_postcode_not_found_error_when_postcode_lookup_cannot_find_the_postcode(self, lookup_mock):
        lookup_mock.return_value = u'{"status":404,"error":"Postcode not found"}'

        with self.assertRaises(geocoder.PostcodeNotFound) as not_found_error:
            geocoder.geocode(self.postcode)
        
        self.assertEqual(not_found_error.exception.postcode, 'sw1a1aa')


class AdviserViewSetTest(django.test.TestCase):

    def setUp(self):
        self.postcode = 'sw1a1aa'
        self.good_result = u'{"status":200,"result":{"postcode":"SW1A 1AA","longitude":-0.141588,"latitude":51.501009}}'

    @mock.patch('lib.PostCodeClient.getLookupPostCode')
    def test_postcode_query_returns_origin_point(self, lookup_mock):
        lookup_mock.return_value = self.good_result

        request = APIRequestFactory().get('/legal-advisers/?postcode=%s' % self.postcode)
        view = AdviserViewSet.as_view({'get': 'list'})
        response = view(request)

        self.assertEqual({
            'postcode': 'SW1A 1AA',
            'point': {
                'type': 'Point',
                'coordinates': [-0.141588, 51.501009]
            }
        }, response.data['origin'])
