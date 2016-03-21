from django.test import TestCase
import mock
import advisers.pc_fallback
import advisers.geocoder


class FallbackTest(TestCase):

    # Test just fallback postcode method
    def test_geocode_fallback(self):

        postcode = 'sw1a1aa'
        result = advisers.pc_fallback.geocode(postcode)

        self.assertIsNotNone(result, 'No result returned for sample postcode')

    # Check that result is obtained from fallback if advisers.geocode fails
    def test_geocode(self):

        with mock.patch('postcodeinfo.Client') as Client:
            client = Client.return_value
            client.lookup_postcode.return_value.valid = False
            postcode = 'sw1a1aa'
            result = advisers.geocoder.geocode(postcode)
            self.assertIsNotNone(result, 'No result returned for sample postcode')
            client.lookup_postcode.assert_called_with(postcode)
