# coding=utf-8

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from advisers.models import Import, IMPORT_STATUSES


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


class UploadTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("test", "test@test.com", "testpassword", is_active=True)

    def test_upload_spreadsheet_success_message(self):
        self.client.login(username="test", password="testpassword")
        Import.objects.create(task_id=1, status=IMPORT_STATUSES.SUCCESS, filename="filename", user=self.user)
        response = self.client.get("/admin/upload/")

        expected_message = "Last import successful"
        self.assertIn(expected_message, response.content.decode("utf-8"))

    def test_upload_spreadsheet_failure_message(self):
        self.client.login(username="test", password="testpassword")
        Import.objects.create(
            task_id=1, status=IMPORT_STATUSES.FAILURE, filename="filename", user=self.user, failure_reason="error"
        )
        response = self.client.get("/admin/upload/")

        expected_message = "Last import failed: error"
        self.assertIn(expected_message, response.content.decode("utf-8"))

    def test_upload_spreadsheet_aborted_message(self):
        self.client.login(username="test", password="testpassword")
        Import.objects.create(
            task_id=1, status=IMPORT_STATUSES.ABORTED, filename="filename", user=self.user, failure_reason="error"
        )
        response = self.client.get("/admin/upload/")

        expected_message = "Last import aborted"
        self.assertIn(expected_message, response.content.decode("utf-8"))

    def test_upload_spreadsheet_running_message(self):
        self.client.login(username="test", password="testpassword")
        Import.objects.create(
            task_id=1, status=IMPORT_STATUSES.RUNNING, filename="filename", user=self.user, failure_reason="error"
        )
        response = self.client.get("/admin/upload/")

        self.assertEqual(response.status_code, 302)

        self.assertEqual(response.url, "/admin/import-in-progress/")
