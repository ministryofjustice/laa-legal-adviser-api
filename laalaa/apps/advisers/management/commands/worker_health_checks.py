import datetime
import sys
import requests
import logging
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from advisers.models import Organisation, Import, IMPORT_STATUSES


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Check access to the database, celery workers and postcodes.io"
    import_created_status_stuck_interval = datetime.timedelta(minutes=10)
    import_running_status_stuck_interval = datetime.timedelta(minutes=60)

    def handle(self, *args, **options):

        try:
            self.check_database_access()
            self.check_import_stuck_in_progress()
            self.check_celery_worker()
            self.check_postcodes_io()
        except Exception as error:
            print(str(error))
            sys.exit(1)

    def check_postcodes_io(self):
        response = requests.get(f"{settings.POSTCODES_IO_URL}/postcodes/SW1A1AA", timeout=5)
        if response.status_code != 200:
            raise CommandError(f"postcodes.io check has failed. Expected 200 response got {response.status_code}")

    def check_database_access(self):
        try:
            # ability to connect to the db; doesn't matter if the result is True or False
            Organisation.objects.exists()
        except Exception:
            raise CommandError("database access check has failed.")

    def check_import_stuck_in_progress(self):
        last_import = Import.get_last()
        if not last_import.is_in_progress():
            return
        if last_import.status == IMPORT_STATUSES.CREATED:
            if last_import.created + self.import_created_status_stuck_interval < timezone.now():
                last_import.abort()
                raise CommandError("Last import is stuck in CREATE status. Import has been aborted")
        if last_import.status == IMPORT_STATUSES.RUNNING:
            if last_import.started + self.import_running_status_stuck_interval < timezone.now():
                last_import.abort()
                raise CommandError("Last import is stuck in RUNNING status. Import has been aborted")

    def check_celery_worker(self):
        stats = self.get_celery_stats()
        if not stats:
            raise CommandError("Celery worker check failed. No running workers were found.")
        try:
            workers = stats.values()
            if not workers:
                raise CommandError("Celery worker check failed. No workers running.")

        except IOError as e:
            raise CommandError(f"Celery worker check failed.  Check that the message broker is running: {str(e)}")

    def get_celery_stats(self):
        from celery import Celery

        app = Celery("laalaa")
        app.config_from_object("django.conf:settings", namespace="CELERY")
        return app.control.inspect().stats()
