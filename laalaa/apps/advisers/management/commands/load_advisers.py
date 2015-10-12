import os
from time import sleep

from django.core.management.base import BaseCommand, CommandError

from advisers.importer import Import


class Command(BaseCommand):
    help = 'Loads the Excel spreadsheet data into the database'
    requires_model_validation = True

    def add_arguments(self, parser):
        parser.add_argument('xlsx_file', help="Excel spreadsheet filename")
        parser.add_argument(
            '--default-transactions', action='store_false',
            dest='single_transaction',
            help="Do not run import in a single transaction")
        parser.add_argument(
            '--force-geocoder', action='store_false', dest='prime_geocoder',
            help="Don't use the postcode locations already stored in DB.")
        parser.add_argument(
            '--dont-clear-db', action='store_false', dest='clear_db',
            help="Prevent DB clear before starting import.")

    def handle(self, *args, **options):
        if not os.path.isfile(options.get('xlsx_file')):
            raise CommandError('Excel spreadsheet filename required')

        importer = Import(options.pop('xlsx_file'), **options)
        try:
            importer.start()

        except Import.Balk:
            return self.warn('Import already running')

        except Import.Fail as failure:
            return self.error('Import failed: {0}'.format(failure))

        try:
            while importer.is_running():
                sleep(1)
                self.stdout.write(importer.progress)

        except KeyboardInterrupt:
            self.stop(importer)

    def warn(self, msg):
        self.stdout.write(msg, style_func=self.style.WARNING)

    def error(self, msg):
        self.stdout.write(msg, style_func=self.style.ERROR)

    def stop(self, importer):
        importer.stop()
        self.stdout.write('Importer stopped')
