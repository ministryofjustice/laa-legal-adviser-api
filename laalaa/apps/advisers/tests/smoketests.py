import os
import unittest

import requests


class Smoketests(unittest.TestCase):

    def test_service_is_up(self):
        try:
            test_url = '{base_url}/legal-advisers/?postcode=sw1h9aj'.format(
                base_url=os.environ.get('SMOKETESTS_BASE_URL'))
            response = requests.get(test_url)
            self.assertStatusCode200(response)
            self.assertValidJson(response)
        except requests.ConnectionError:
            self.fail('Failed to connect to: {url}'.format(
                url=os.environ.get('SMOKETESTS_BASE_URL')))

    def assertStatusCode200(self, response):
        self.assertEqual(200, response.status_code, (
            'Response code not 200: {0.status_code}'.format(response)))

    def assertValidJson(self, response):
        try:
            first_result = response.json()['results'][0]
            coords = first_result['location']['point']['coordinates']
            self.assertEqual(2, len(coords), (
                'Response not valid JSON'))
        except:
            self.fail('Response not valid JSON')
