# -*- coding: utf-8 -*-
import sys
from django.core.management.base import BaseCommand

from advisers.importer import AdviserImport


class Command(BaseCommand):

    help = 'Load Advisers from old xls file'
    requires_model_validation = True

    def handle(self, *args, **options):

        if len(args) < 1:
            self.stdout.write("Must pass path to xls files as first arg")
            sys.exit(-1)

        path = args[0]

        importer = AdviserImport(path)
