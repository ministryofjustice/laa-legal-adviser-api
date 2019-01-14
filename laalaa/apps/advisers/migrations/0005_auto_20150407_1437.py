# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("advisers", "0004_auto_20150407_1228")]

    operations = [
        migrations.RemoveField(model_name="category", name="firm"),
        migrations.AddField(
            model_name="office",
            name="categories",
            field=models.ManyToManyField(to="advisers.Category"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="outreachservice",
            name="categories",
            field=models.ManyToManyField(to="advisers.Category"),
            preserve_default=True,
        ),
    ]
