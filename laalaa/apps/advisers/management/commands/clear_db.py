from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Clears advisers data'
    requires_model_validation = True

    def handle(self, *args, **options):
        cursor = connection.cursor()

        def clear(table):
            cursor.execute('DELETE FROM advisers_%s' % table)
            cursor.execute(
                'ALTER SEQUENCE advisers_%s_id_seq RESTART WITH 1' % table)

        clear('outreachservice')
        clear('outreachtype')
        clear('office')
        clear('organisation')
        clear('organisationtype')
        clear('location')
