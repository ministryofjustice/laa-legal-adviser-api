import json
import mock
import unittest

import django.test
import postcodeinfo
from rest_framework.test import APIRequestFactory

from advisers import geocoder
from advisers.views import AdviserViewSet

from advisers import pc_fallback


class GeocoderTest(unittest.TestCase):


    def test_geocode(self):

        with mock.patch('postcodeinfo.Client') as Client:
            client = Client.return_value

            postcode = 'sw1a1aa'
            geocoder.geocode(postcode)

            client.lookup_postcode.assert_called_with(postcode)

    def test_geocode_no_results(self):
        import postcodeinfo

        with mock.patch.object(postcodeinfo.Client, '_query_api') as _query_api:
            def no_results(*args, **kwargs):
                raise postcodeinfo.NoResults

            _query_api.side_effect = no_results

            postcode = 'sw1a1aa'
            with self.assertRaises(geocoder.PostcodeNotFound) as context:
                geocoder.geocode(postcode)

            self.assertEqual(postcode, context.exception.postcode)

    def test_geocode_server_error(self):
        with mock.patch('postcodeinfo.Client') as Client:
            client = Client.return_value

            def server_error(exception):

                def lookup_postcode(postcode):
                    raise exception

                return lookup_postcode

            postcode = 'sw1a1aa'
            for exception in [
                    postcodeinfo.ServerException,
                    postcodeinfo.ServiceUnavailable]:

                client.lookup_postcode.side_effect = server_error(exception)

                with self.assertRaises(geocoder.GeocoderError):
                    geocoder.geocode(postcode)


class AdviserViewSetTest(django.test.TestCase):

    def test_geocode(self):
        with mock.patch('postcodeinfo.Client') as Client:
            postcode = 'sw1a1aa'
            client = Client.return_value
            info = client.lookup_postcode.return_value
            info.longitude = -0.1442833
            info.latitude = 51.5016681
            info.postcode = 'SW1A 1AA'

            request = APIRequestFactory().get(
                '/legal-advisers/?postcode=%s' % postcode)
            view = AdviserViewSet.as_view({'get': 'list'})
            response = view(request)

            client.lookup_postcode.assert_called_with(postcode)
            origin = response.data['origin']
            self.assertEqual(info.postcode, origin['postcode'])
            coords = origin['point']['coordinates']
            self.assertEqual(info.longitude, coords[0])
            self.assertEqual(info.latitude, coords[1])
