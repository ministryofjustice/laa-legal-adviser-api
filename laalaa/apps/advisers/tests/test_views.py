# coding=utf-8

import os
from django.contrib.auth.models import User
from django.test import TestCase, override_settings, RequestFactory
from django.test.client import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from advisers.models import Import, IMPORT_STATUSES
from advisers.views import save_file


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

    def test_upload_spreadsheet_created_message(self):
        self.client.login(username="test", password="testpassword")
        Import.objects.create(
            task_id=1, status=IMPORT_STATUSES.CREATED, filename="filename", user=self.user, failure_reason="error"
        )
        response = self.client.get("/admin/upload/")

        self.assertEqual(response.status_code, 302)

        self.assertEqual(response.url, "/admin/import-in-progress/")

    def test_upload_spreadsheet_running_message(self):
        self.client.login(username="test", password="testpassword")
        Import.objects.create(
            task_id=1, status=IMPORT_STATUSES.RUNNING, filename="filename", user=self.user, failure_reason="error"
        )
        response = self.client.get("/admin/upload/")

        self.assertEqual(response.status_code, 302)

        self.assertEqual(response.url, "/admin/import-in-progress/")


class SaveFileTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # Ensure the test temp directory exists
        if not os.path.exists("/tmp/test_uploads"):
            os.makedirs("/tmp/test_uploads")

    @override_settings(TEMP_DIRECTORY="/tmp/test_uploads")
    def test_save_file_normal_behavior(self):
        """Test that a valid file is saved correctly to the temp directory."""
        file_content = b"test content"
        uploaded_file = SimpleUploadedFile("spreadsheet.xlsx", file_content)

        request = self.factory.post("/", {"xlfile": uploaded_file})
        request.FILES["xlfile"] = uploaded_file

        result_path = save_file(request)

        # Assertions
        self.assertTrue(os.path.exists(result_path))
        self.assertTrue(result_path.endswith("spreadsheet.xlsx"))
        with open(result_path, "rb") as f:
            self.assertEqual(f.read(), file_content)

        os.remove(result_path)

    @override_settings(TEMP_DIRECTORY="/tmp/test_uploads")
    def test_save_file_traversal_attack(self):
        """Test that directory traversal attempts are neutralized."""
        file_content = b"malicious content"
        # The 'name' contains a traversal attempt
        malicious_name = "../../../etc/passwd"
        uploaded_file = SimpleUploadedFile(malicious_name, file_content)

        request = self.factory.post("/", {"xlfile": uploaded_file})
        request.FILES["xlfile"] = uploaded_file

        result_path = save_file(request)

        # Assert that the file was NOT saved in /etc/passwd
        # and instead stayed within the TEMP_DIRECTORY
        self.assertIn(settings.TEMP_DIRECTORY, result_path)
        self.assertEqual(os.path.basename(result_path), "passwd")
        self.assertNotIn("..", result_path)

        os.remove(result_path)

    @override_settings(TEMP_DIRECTORY="/tmp/test_uploads")
    def test_save_file_with_complex_path_name(self):
        """Test that nested paths in filename are stripped."""
        uploaded_file = SimpleUploadedFile("folder/subfolder/data.csv", b"content")
        request = self.factory.post("/", {"xlfile": uploaded_file})
        request.FILES["xlfile"] = uploaded_file

        result_path = save_file(request)

        # Should only keep 'data.csv'
        self.assertEqual(os.path.basename(result_path), "data.csv")

        os.remove(result_path)
