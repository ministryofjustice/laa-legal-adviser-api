import json
import mock
import unittest

import django.test
import postcodeinfo
from rest_framework.test import APIRequestFactory

from advisers import geocoder
from advisers.views import AdviserViewSet

import advisers.pc_fallback


class FallbackTest(django.test.Testcase):

   def test_geocode_fallback(self):

        with mock.patch('postcodes.PostCoder') as PostCoder:

            fallback_client = PostCoder.return_value

            postcode = 'sw1a1aa'
            advisers.pc_fallback.geocode(postcode)

            fallback_client.get.assert_called_with(postcode)

#if __name__ == '__main__':
#    unittest.main()