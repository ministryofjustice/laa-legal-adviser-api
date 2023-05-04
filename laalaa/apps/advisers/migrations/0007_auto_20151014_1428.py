# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import models, migrations
from django.core import serializers


fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../fixtures"))
fixture_filename = "initial_categories.json"


def load_fixture(apps, schema_editor):
    fixture_file = os.path.join(fixture_dir, fixture_filename)

    fixture = open(fixture_file, "rb")
    objects = serializers.deserialize("json", fixture, ignorenonexistent=True)
    for obj in objects:
        obj.save()
    fixture.close()


def unload_fixture(apps, schema_editor):
    "Brutally deleting all entries for this model..."

    for m in ["location", "organisationtype", "outreachtype", "category"]:
        Mod = apps.get_model("advisers", m)
        Mod.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("advisers", "0006_import")]

    operations = [
        migrations.RunSQL("TRUNCATE advisers_location RESTART IDENTITY CASCADE;"),
        migrations.RunSQL("TRUNCATE advisers_organisationtype RESTART IDENTITY CASCADE;"),
        migrations.RunSQL("TRUNCATE advisers_outreachtype RESTART IDENTITY CASCADE;"),
        migrations.RunSQL("TRUNCATE advisers_category RESTART IDENTITY CASCADE;"),
        migrations.AlterField(
            model_name="office",
            name="location",
            field=models.OneToOneField(null=True, to="advisers.Location", on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="outreachservice",
            name="location",
            field=models.OneToOneField(null=True, to="advisers.Location", on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.RunPython(load_fixture, reverse_code=unload_fixture),
    ]
