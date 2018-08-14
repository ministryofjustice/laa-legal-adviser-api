import json
import mock
import unittest
import django.test
import requests
import responses

from rest_framework.test import APIRequestFactory
from advisers import geocoder
from advisers import models
from advisers.views import AdviserViewSet
from django.contrib.gis import db


class GeocoderTest(unittest.TestCase):

    def setUp(self):
        self.postcode = 'sw1a1aa'
        self.good_result = {'status':200,'result':[{'postcode':'SW1A 1AA','longitude':-0.141588,'latitude':51.501009}]}


    @responses.activate
    def test_geocode_strips_spaces_before_calling_external_api(self):
        responses.add(responses.GET, 'https://api.postcodes.io/postcodes/?q=sw1a1aa&limit=1',
            match_querystring=True, json=self.good_result, status=200)
        geocoder.geocode('SW1A 1AA')
        self.assertEqual(len(responses.calls), 1)


    @mock.patch('advisers.geocoder.lookup_postcode')
    def test_geocode_calls_postcode_lookup(self, lookup_mock):
        lookup_mock.return_value = self.good_result
        result = geocoder.geocode(self.postcode)

        self.assertEqual(result.postcode, 'sw1a1aa')
        self.assertEqual(result.latitude, 51.501009)
        self.assertEqual(result.longitude, -0.141588)


    @mock.patch('advisers.geocoder.lookup_postcode')
    def test_raises_geocoder_error_when_postcode_lookup_fails_with_timeout(self, lookup_mock):
        lookup_mock.side_effect = requests.exceptions.ConnectTimeout()

        with self.assertRaisesRegexp(geocoder.GeocoderError, 'Caused by ConnectTimeout'):
            geocoder.geocode(self.postcode)


    @mock.patch('advisers.geocoder.lookup_postcode')
    def test_raises_geocoder_error_when_postcode_lookup_fails_with_server_error(self, lookup_mock):
        lookup_mock.return_value = {"status":500,"message":"Bad things happened"}

        with self.assertRaisesRegexp(geocoder.GeocoderError, 'Bad things happened'):
            geocoder.geocode(self.postcode)


    @mock.patch('advisers.geocoder.lookup_postcode')
    def test_raises_geocoder_error_when_postcode_lookup_fails_with_client_error(self, lookup_mock):
        lookup_mock.return_value = {"status":400,"message":"Invalid request"}

        with self.assertRaisesRegexp(geocoder.GeocoderError, 'Invalid request'):
            geocoder.geocode(self.postcode)


    @mock.patch('advisers.geocoder.lookup_postcode')
    def test_raises_postcode_not_found_error_when_postcode_lookup_cannot_find_the_postcode(self, lookup_mock):
        lookup_mock.return_value = {"status":404,"error":"Postcode not found"}

        with self.assertRaises(geocoder.PostcodeNotFound) as not_found_error:
            geocoder.geocode(self.postcode)
        
        self.assertEqual(not_found_error.exception.postcode, 'sw1a1aa')


class AdviserViewSetTest(django.test.TestCase):

    def setUp(self):
        self.postcode = 'ex3ple'
        self.good_result = {"status":200,"result":[{"postcode":"EX3 PLE","longitude":0.0,"latitude":51.15}]}
        self.request = APIRequestFactory().get('/legal-advisers/?postcode=%s' % self.postcode)
        self.view = AdviserViewSet.as_view({'get': 'list'})


    @mock.patch('advisers.geocoder.lookup_postcode')
    def test_postcode_query_returns_origin_point(self, lookup_mock):
        lookup_mock.return_value = self.good_result
        response = self.view(self.request)

        self.assertEqual({
            'postcode': 'EX 3PLE',
            'point': {
                'type': 'Point',
                'coordinates': [0.0, 51.15]
            }
        }, response.data['origin'])


    def create_test_location(self):
        category = models.Category.objects.get(code='CRM')
        org_type = models.OrganisationType.objects.get(name='Solicitor')

        org = models.Organisation.objects.create(
            firm=99999, name='Example Legal Aid Provider', website='http://example.org', type=org_type)

        loc = models.Location.objects.create(
            postcode='EX3 PL3', city='Test Town', address='Test Address', point='POINT (0.001 51.005)')

        office = models.Office.objects.create(
            telephone='0200 000 0000', location=loc, organisation=org)
        office.categories = [category]
        office.save()


    @mock.patch('advisers.geocoder.lookup_postcode')
    def test_postcode_query_returns_valid_results(self, lookup_mock):
        self.create_test_location()
        lookup_mock.return_value = self.good_result
        response = self.view(self.request)

        self.assertEqual({
            'telephone': '0200 000 0000',
            'location': {
                'address': 'Test Address',
                'city': 'Test Town',
                'postcode': 'EX3 PL3',
                'point': {
                    'type': 'Point',
                    'coordinates': [0.001, 51.005]
                },
                'type': 'Office'
            },
            'organisation': {
                'name': 'Example Legal Aid Provider',
                'website': 'http://example.org'
            },
            'distance': 10.01863983643646, # miles
            'categories': ['CRM']
        }, response.data['results'][0])
