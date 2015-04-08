# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisers', '0003_organisation_firm'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='civil',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='category',
            name='firm',
            field=models.ForeignKey(to='advisers.Organisation', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='category',
            name='code',
            field=models.CharField(max_length=8),
            preserve_default=True,
        ),
    ]
