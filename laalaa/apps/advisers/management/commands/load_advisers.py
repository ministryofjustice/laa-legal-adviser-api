from optparse import make_option
from time import sleep

from django.core.management.base import BaseCommand, CommandError

from advisers.importer import ImportProcess


class Command(BaseCommand):
    args = '<excel filename>'
    help = 'Loads the Excel spreadsheet data into the database'
    requires_model_validation = True
    option_list = BaseCommand.option_list + (
        make_option('--default-transactions', action='store_false', dest='single_transaction', default=True,
                    help='Do not run import in a single transaction.'),
        make_option('--force-geocoder', action='store_false', dest='prime_geocoder', default=True,
                    help="Don't use the postcode locations already stored in DB."),
        make_option('--dont-clear-db', action='store_false', dest='clear_db', default=True,
                    help='Prevent DB clear before starting import.'),
    )

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError('Excel spreadsheet filename required')

        try:
            importer = ImportProcess(args[0], options['prime_geocoder'],
                                     options['clear_db'], options['single_transaction'])
            importer.start()

            try:
                while importer.is_alive() and importer.progress['task'] is not None:
                    sleep(1)
                    self.stdout.write('{task}'.format(**importer.progress), ending=' ')
                    if 'total' in importer.progress:
                        self.stdout.write('\b: {count} / {total}'.format(**importer.progress))
                    else:
                        self.stdout.write('')
            except KeyboardInterrupt:
                self.stdout.write('Interrupting importer thread', style_func=self.style.WARNING)
                importer.interrupt()
                importer.join()
                self.stdout.write('Importer stopped')

        except Exception as e:
            raise CommandError('Failed opening Excel spreadsheet: %s' % e)
