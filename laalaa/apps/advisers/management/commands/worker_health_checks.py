import sys
import requests
import logging
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from advisers.models import Organisation


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Check access to the database, celery workers and postcodes.io "

    def handle(self, *args, **options):

        try:
            self.check_database_access()
            self.check_celery_worker()
            self.check_postcodes_io()
        except Exception:
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

    def check_celery_worker(self):
        from celery import Celery

        app = Celery("laalaa")
        app.config_from_object("django.conf:settings", namespace="CELERY")
        stats = app.control.inspect().stats()
        if not stats:
            raise CommandError("Celery worker check failed. No running workers were found.")
        try:
            workers = stats.values()
            if not workers:
                raise CommandError("Celery worker check failed. No workers running.")

        except IOError as e:
            raise CommandError(f"Celery worker check failed.  Check that the message broker is running: {str(e)}")
