# coding=utf-8

import datetime
from django.test import TestCase
from advisers.models import Import, IMPORT_STATUSES
from unittest.mock import patch, Mock, MagicMock
from django.contrib.auth.models import User
from django.core.management.base import CommandError
from advisers.management.commands.worker_health_checks import Command


class WorkerHealthCheckCommandTestCase(TestCase):
    def setUp(self):
        self.command = Command()
        self.user = User.objects.create_user("test", "test@test.com", "testpassword", is_active=True)

    def test_check_import_stuck_in_progress__created(self):
        Import.objects.create(task_id=1, status=IMPORT_STATUSES.CREATED, filename="filename", user=self.user)
        self.command.check_import_stuck_in_progress()
        self.command.import_created_status_stuck_interval = datetime.timedelta(minutes=-20)
        with self.assertRaisesMessage(CommandError, "Last import is stuck in CREATE status. Import has been aborted"):
            self.command.check_import_stuck_in_progress()
        self.assertEqual(Import.get_last().status, IMPORT_STATUSES.ABORTED)

    def test_check_import_stuck_in_progress__running(self):
        Import.objects.create(task_id=1, status=IMPORT_STATUSES.CREATED, filename="filename", user=self.user)
        last_import = Import.get_last()
        last_import.start()
        self.command.import_running_status_stuck_interval = datetime.timedelta(minutes=30)
        self.command.check_import_stuck_in_progress()
        self.command.import_running_status_stuck_interval = datetime.timedelta(minutes=-60)
        with self.assertRaisesMessage(CommandError, "Last import is stuck in RUNNING status. Import has been aborted"):
            self.command.check_import_stuck_in_progress()
        self.assertEqual(Import.get_last().status, IMPORT_STATUSES.ABORTED)

    def test_check_celery_worker_failure_workers(self):
        def mock_celery_get_stats():
            stats = Mock()
            stats.values = MagicMock(return_value=False)
            return stats

        with patch.object(self.command, "get_celery_stats", mock_celery_get_stats):
            with self.assertRaisesMessage(CommandError, "Celery worker check failed. No workers running."):
                self.command.check_celery_worker()

    def test_check_celery_worker_failure_broker(self):
        def mock_celery_get_stats():
            stats = Mock()
            stats.values = MagicMock(side_effect=IOError)
            return stats

        with patch.object(self.command, "get_celery_stats", mock_celery_get_stats):
            with self.assertRaisesRegex(
                CommandError, r"^Celery worker check failed.  Check that the message broker is running:"
            ):
                self.command.check_celery_worker()
