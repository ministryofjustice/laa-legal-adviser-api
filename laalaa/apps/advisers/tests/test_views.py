# coding=utf-8

from django.test import TestCase


class CategoriesOfLawTestCase(TestCase):
    def setUp(self, *args, **kwargs):
        super(CategoriesOfLawTestCase, self).setUp(*args, **kwargs)

    def test_categories_of_law_api(self):
        response = self.client.get("/categories_of_law/")
        self.assertEqual(response.status_code, 200)

        expected_civil = dict(code="MHE", civil=True, name="Mental health")
        expected_crime = dict(code="CRM", civil=False, name="Crime")
        self.assertIn(expected_civil, response.data)
        self.assertIn(expected_crime, response.data)
