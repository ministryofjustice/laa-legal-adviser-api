from django.core.management.base import BaseCommand
from advisers.models import Import


class Command(BaseCommand):
    help = "Abort last Import job"

    def handle(self, *args, **options):
        Import.abort_last()
