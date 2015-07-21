import os
import sys

from django.core.management.base import BaseCommand
from django.test.runner import DiscoverRunner


class Command(BaseCommand):
    help = 'Run the smoketests'

    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument(
            'base_url', action='store', required=True,
            help='The base URL of the service to run smoketests against')

    def handle(self, base_url, *args, **kwargs):
        os.environ['SMOKETESTS_BASE_URL'] = base_url.rstrip('/')
        test_runner = DiscoverRunner(pattern='smoketests.py')
        failures = test_runner.run_tests([])
        if failures:
            sys.exit(bool(failures))
