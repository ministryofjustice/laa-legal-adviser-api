import sys

from django.core.management.base import BaseCommand

from advisers.models import Organisation


class Command(BaseCommand):
    help = "Attempts to establish connections with vital services and raises an error if this is not possible"

    def handle(self, *args, **options):
        try:
            # ability to connect to the db; doesn't matter if the result is True or False
            Organisation.objects.exists()
        except Exception:
            sys.exit(1)
