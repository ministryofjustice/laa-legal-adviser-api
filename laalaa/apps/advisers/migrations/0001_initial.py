# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("code", models.CharField(max_length=48)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Location",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("address", models.CharField(max_length=255)),
                ("city", models.CharField(max_length=48)),
                ("postcode", models.CharField(max_length=16)),
                ("point", django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Office",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("telephone", models.CharField(max_length=48)),
                ("account_number", models.CharField(unique=True, max_length=10)),
                ("location", models.ForeignKey(to="advisers.Location")),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Organisation",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("name", models.CharField(max_length=255)),
                ("website", models.URLField(null=True, blank=True)),
                ("contracted", models.BooleanField(default=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="OrganisationType",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("name", models.CharField(max_length=48)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="OutreachService",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("location", models.ForeignKey(to="advisers.Location")),
                ("office", models.ForeignKey(to="advisers.Office")),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="OutreachType",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("name", models.CharField(max_length=48)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="outreachservice",
            name="type",
            field=models.ForeignKey(to="advisers.OutreachType"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="organisation",
            name="type",
            field=models.ForeignKey(to="advisers.OrganisationType"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="office",
            name="organisation",
            field=models.ForeignKey(to="advisers.Organisation"),
            preserve_default=True,
        ),
    ]
