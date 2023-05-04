# Generated by Django 2.2.10 on 2021-08-11 16:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("advisers", "0008_import_task_id")]

    operations = [
        migrations.AlterField(
            model_name="import",
            name="status",
            field=models.CharField(
                choices=[
                    ("RUNNING", "running"),
                    ("SUCCESS", "success"),
                    ("FAILURE", "failure"),
                    ("ABORTED", "aborted"),
                ],
                max_length=7,
            ),
        ),
        migrations.AlterField(model_name="import", name="task_id", field=models.CharField(default="", max_length=50)),
    ]
