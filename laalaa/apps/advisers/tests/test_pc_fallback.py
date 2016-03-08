import unittest

import advisers.pc_fallback


class FallbackTest(unittest.TestCase):

    def test_geocode_fallback(self):

            postcode = 'sw1a1aa'
            result = advisers.pc_fallback.geocode(postcode)

            self.assertIsNotNone(result, 'No result returned for sample postcode')

    def test_formatter(self):

            formatted_pc = advisers.pc_fallback.format_postcode('SW1A 1AA')

            self.assertNotIn(' ', formatted_pc, 'Formatted postcode has space')
            self.assertNotIn('AA', formatted_pc, 'Formatted postcode has AA')
            self.assertIn('aa', formatted_pc, 'Formatted postcode does not have aa')

if __name__ == '__main__':
    unittest.main()
