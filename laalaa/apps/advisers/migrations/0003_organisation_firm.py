# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [("advisers", "0002_auto_20150330_1507")]

    operations = [
        migrations.AddField(
            model_name="organisation", name="firm", field=models.IntegerField(null=True), preserve_default=True
        )
    ]
