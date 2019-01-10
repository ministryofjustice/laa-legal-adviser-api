# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("advisers", "0007_auto_20151014_1428")]

    operations = [
        migrations.AddField(
            model_name="import",
            name="task_id",
            field=models.CharField(default=b"", max_length=50),
            preserve_default=True,
        )
    ]
