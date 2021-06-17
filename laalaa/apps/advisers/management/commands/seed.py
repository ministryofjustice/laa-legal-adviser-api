import os

from django.core.management.base import BaseCommand
from django.core import serializers
from advisers import models


class Command(BaseCommand):
    help = "Seeds the initial set of data for adviser locations, offices, etc."
    fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../fixtures"))
    fixture_filename = "initial_advisers.json"

    def handle(self, *args, **options):
        if models.Location.objects.count() > 0:
            print("Database already contains adviser data. Skipping seeding initial data.")
            return

        fixture_file = os.path.join(self.fixture_dir, self.fixture_filename)
        fixture = open(fixture_file, "rb")
        objects = list(serializers.deserialize("json", fixture, ignorenonexistent=True))

        print("Importing {} objects from {}".format(len(objects), fixture_file))
        progress = 0
        for obj in objects:
            obj.save()
            progress = progress + 1
            if progress % 1000 == 0:
                print("{}...".format(progress))

        fixture.close()
        print("Done!")
