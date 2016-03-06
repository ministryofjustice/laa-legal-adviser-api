# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisers', '0008_import_task_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='TemporaryPostcodes',
            fields=[
                ('postcode_index', models.CharField(max_length=7, serialize=False, primary_key=True, db_index=True)),
                ('latitude', models.FloatField(null=True)),
                ('longitude', models.FloatField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
