from django.core.management.base import NoArgsCommand
from django.db import connection


class Command(NoArgsCommand):
    help = 'Clears advisers data'
    requires_model_validation = True

    def handle_noargs(self, **options):
        cursor = connection.cursor()

        def clear(table):
            cursor.execute('DELETE FROM advisers_%s' % table)
            cursor.execute(
                'ALTER SEQUENCE advisers_%s_id_seq RESTART WITH 1' % table)

        clear('outreachservice_categories')
        clear('outreachservice')
        clear('outreachtype')
        clear('office_categories')
        clear('office')
        clear('organisation')
        clear('organisationtype')
        clear('location')
