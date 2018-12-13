# coding=utf-8
from __future__ import absolute_import

import os

from raven.contrib.celery import register_logger_signal
from raven.scripts.runner import send_test_message
from celery import Celery

# set the default Django settings module for the 'celery' program.

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "laalaa.settings")

from django.conf import settings  # noqa

app = Celery("laalaa")

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

client = None
if hasattr(settings, "RAVEN_CONFIG"):
    from raven.contrib.django.models import client

    register_logger_signal(client)
    register_logger_signal(client)


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))


@app.task()
def sentry_test_task():
    if client:
        send_test_message(client, {})
