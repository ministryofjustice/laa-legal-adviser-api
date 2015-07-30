from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from advisers.importer import ImportShellRun


class Command(BaseCommand):
    args = '<excel filename>'
    help = 'Loads the Excel spreadsheet data into the database'
    requires_model_validation = True
    option_list = BaseCommand.option_list + (
        make_option('--force-geocoder', action='store_false', dest='prime_geocoder', default=True,
                    help="Don't use the postcode locations already stored in DB."),
    )

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError('Excel spreadsheet filename required')
        try:
            importer = ImportShellRun()
            importer(args[0], should_prime_geocoder=options['prime_geocoder'])
        except Exception as e:
            raise CommandError('Failed opening Excel spreadsheet: %s' % e)
