# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):
    dependencies = [("advisers", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="location",
            name="point",
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, null=True),
            preserve_default=True,
        )
    ]
