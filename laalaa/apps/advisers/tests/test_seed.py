from django.core.management import call_command
from django.test import TestCase

from advisers import models, tasks


class SeedTest(TestCase):
    def test_seed_loads_models_with_organisation_type(self):
        tasks.clear_db()
        call_command("seed")
        # OrganisationType model loaded from initial_categories.json
        self.assertGreater(models.OrganisationType.objects.count(), 0)
        # Location model loaded from initial_advisers.json
        self.assertGreater(models.Location.objects.count(), 0)
