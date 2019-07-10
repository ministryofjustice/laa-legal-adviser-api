import sys

from django.core.management.base import BaseCommand

from advisers.tasks import check_workers


class Command(BaseCommand):
    help = "Checks that there are celery workers running"

    def handle(self, *args, **options):
        if not check_workers():
            sys.exit(1)
