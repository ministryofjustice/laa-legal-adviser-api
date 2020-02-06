# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ("advisers", "0005_auto_20150407_1437")]

    operations = [
        migrations.CreateModel(
            name="Import",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("started", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        max_length=7,
                        choices=[
                            (b"RUNNING", b"running"),
                            (b"SUCCESS", b"success"),
                            (b"FAILURE", b"failure"),
                            (b"ABORTED", b"aborted"),
                        ],
                    ),
                ),
                ("filename", models.TextField()),
                ("user", models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
            ],
            options={},
            bases=(models.Model,),
        )
    ]
