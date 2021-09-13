# coding=utf-8

import datetime
from django.test import TestCase
from advisers.models import Import, IMPORT_STATUSES
from unittest.mock import patch
from django.utils import timezone
from django.contrib.auth.models import User


class ImportModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test", "test@test.com", "testpassword", is_active=True)

    def test_abort_last_import(self):
        Import.objects.create(task_id=1, status=IMPORT_STATUSES.CREATED, filename="filename", user=self.user)
        last = Import.objects.abort_last()
        self.assertIsInstance(last, Import)
        self.assertEqual(last.status, IMPORT_STATUSES.ABORTED)

    def test_abort_last_import__no_imports(self):
        self.assertIsNone(Import.objects.abort_last())

    def test_is_in_progress(self):
        last_import = Import.objects.create(
            task_id=1, status=IMPORT_STATUSES.CREATED, filename="filename", user=self.user
        )
        self.assertTrue(last_import.is_in_progress())

        last_import = Import.objects.create(
            task_id=1, status=IMPORT_STATUSES.RUNNING, filename="filename", user=self.user
        )
        self.assertTrue(last_import.is_in_progress())

        last_import = Import.objects.create(
            task_id=1, status=IMPORT_STATUSES.SUCCESS, filename="filename", user=self.user
        )
        self.assertFalse(last_import.is_in_progress())

    @patch("django.utils.timezone.now")
    def test_start_import(self, mock_timezone):
        mock_timezone.return_value = datetime.datetime(2021, 9, 2, tzinfo=timezone.utc)
        last_import = Import.objects.create(
            task_id=1, status=IMPORT_STATUSES.CREATED, filename="filename", user=self.user
        )
        last_import.start()
        self.assertEqual(mock_timezone.return_value, last_import.started)
        self.assertTrue(last_import.status == IMPORT_STATUSES.RUNNING)

    @patch("django.utils.timezone.now")
    def test_complete_import(self, mock_timezone):
        mock_timezone.return_value = datetime.datetime(2021, 9, 2, tzinfo=timezone.utc)
        last_import = Import.objects.create(
            task_id=1, status=IMPORT_STATUSES.RUNNING, filename="filename", user=self.user
        )
        last_import.complete()
        self.assertEqual(mock_timezone.return_value, last_import.completed)
        self.assertTrue(last_import.status == IMPORT_STATUSES.SUCCESS)
