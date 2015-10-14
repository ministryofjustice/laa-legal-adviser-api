# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisers', '0006_import'),
    ]

    operations = [
        migrations.AlterField(
            model_name='office',
            name='location',
            field=models.OneToOneField(null=True, to='advisers.Location'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='outreachservice',
            name='location',
            field=models.OneToOneField(null=True, to='advisers.Location'),
            preserve_default=True,
        ),
    ]
