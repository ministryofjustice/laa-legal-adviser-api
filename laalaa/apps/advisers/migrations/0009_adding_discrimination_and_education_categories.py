# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-30 16:16
from __future__ import unicode_literals

from django.db import migrations
from django.db import connection


def create_discrimination_and_education_categories(apps, schema_editor):
    Category = apps.get_model("advisers", "Category")
    # Hard coding the id values as this is referenced in advisers/fixtures
    Category.objects.get_or_create(id=14, code="DISC", defaults={"civil": True})
    Category.objects.get_or_create(id=15, code="EDU", defaults={"civil": True})

    # This is required because the id field is specified in the fixtures (and above) and has become out of sync with
    # next sequence value
    sql = 'SELECT setval(pg_get_serial_sequence(\'advisers_category\',\'id\'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "advisers_category";'
    connection.cursor().execute(sql)


class Migration(migrations.Migration):

    dependencies = [("advisers", "0008_import_task_id")]

    operations = [migrations.RunPython(create_discrimination_and_education_categories)]
