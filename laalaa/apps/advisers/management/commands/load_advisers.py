from django.core.management.base import BaseCommand, CommandError

from advisers.importer import AdviserImport


class Command(BaseCommand):
    args = '<excel filename>'
    help = 'Loads the Excel spreadsheet data into the database'
    requires_model_validation = True

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError('Excel spreadsheet filename required')

        try:
            importer = AdviserImport(args[0])
        except Exception as e:
            raise CommandError('Failed opening Excel spreadsheet: %s' % e)

        importer.import_all()
