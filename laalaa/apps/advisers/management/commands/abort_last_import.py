from django.core.management.base import BaseCommand
from advisers.models import Import
from .utils import AbortImportMixin


class Command(BaseCommand, AbortImportMixin):
    help = "Abort last Import job"

    def handle(self, *args, **options):
        last = Import.objects.last()
        if last:
            if last.is_in_progress():
                self.stdout.write("Aborting import {}".format(last.pk))
                self.abort_import(last)
            else:
                self.stderr.write("Not aborting import {} with status {}".format(last.pk, last.status))
        else:
            self.stderr.write("Could not find any import to attempt to abort")
