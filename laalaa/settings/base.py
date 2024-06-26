"""
Django settings for laalaa project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from os.path import join, abspath, dirname
import sys

import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


def here(*x):
    return join(abspath(dirname(__file__)), *x)


PROJECT_ROOT = here("..")


def root(*x):
    return join(abspath(PROJECT_ROOT), *x)


sys.path.insert(0, root("apps"))

# See https://github.com/ministryofjustice/django-moj-irat#usage for usage
HEALTHCHECKS = ["moj_irat.healthchecks.database_healthcheck"]
AUTODISCOVER_HEALTHCHECKS = True

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "DEV_KEY")

DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django_celery_results",
    "rest_framework",
    "rest_framework_gis",
    "advisers",
    "categories",
    "django_prometheus",
)

MIDDLEWARE = (
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "advisers.middleware.PingMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
    # Prometheus should maybe be before the cache, so that we know when the URL has been accessed
    # but it didn't seem to work at all
    "django_prometheus.middleware.PrometheusAfterMiddleware",
)

ROOT_URLCONF = "laalaa.urls"

WSGI_APPLICATION = "laalaa.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [root("templates")],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(
        env="DATABASE_URL",
        default="postgis://postgres@127.0.0.1:5432/laalaa",
        engine="django.contrib.gis.db.backends.postgis",
    )
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = "en-gb"

TIME_ZONE = "Europe/London"

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = root("uploads")
MEDIA_URL = "/uploads/"
# 10MB
MAX_UPLOAD_SIZE = 10485760
# Force uploaded files to be written to disk
FILE_UPLOAD_MAX_MEMORY_SIZE = 0

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
if os.environ.get("STATIC_FILES_BACKEND") == "s3":
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_DEFAULT_ACL = None

STATIC_URL = "/static/"
STATIC_ROOT = root("static")

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "EXCEPTION_HANDLER": "advisers.views.custom_exception_handler",
}

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": root("cache")}}

CACHE_MIDDLEWARE_SECONDS = 3600

CELERY_ACCEPT_CONTENT = ["pickle", "json", "msgpack"]
CELERY_ENABLE_UTC = True  # I think this is the default now anyway
CELERY_RESULT_BACKEND = "django-db"
CELERY_IGNORE_RESULT = True  # SQS doesn't support it
CELERY_MESSAGE_COMPRESSION = "gzip"  # got to look after the pennies
CELERY_DISABLE_RATE_LIMITS = True  # they don't work with SQS
CELERY_ENABLE_REMOTE_CONTROL = False  # doesn't work well under docker
CELERY_TIMEZONE = "UTC"

CELERY_BROKER_TRANSPORT_OPTIONS = {
    "polling_interval": 10,
    "region": os.environ.get("SQS_REGION", "eu-west-2"),
    "wait_time_seconds": 20,
}

if os.environ.get("CELERY_PREDEFINED_QUEUE_URL"):
    predefined_queue_url = os.environ.get("CELERY_PREDEFINED_QUEUE_URL")
    CELERY_BROKER_URL = "sqs://"
    CELERY_DEFAULT_QUEUE = predefined_queue_url.split("/")[-1]
    CELERY_CREATE_MISSING_QUEUES = False
    CELERY_BROKER_TRANSPORT_OPTIONS["predefined_queues"] = {"celery": {"url": predefined_queue_url}}
else:
    # if no BROKER_URL specified then don't try to use celery
    # because it'll just cause errors
    CELERY_ALWAYS_EAGER = True


TEMP_DIRECTORY = root("tmp")

POSTCODES_IO_URL = "https://api.postcodes.io"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"},
        "simple": {"format": "%(levelname)s %(message)s"},
        "logstash": {"()": "logstash_formatter.LogstashFormatter"},
    },
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        }
    },
    "loggers": {"django.request": {"handlers": ["mail_admins"], "level": "ERROR", "propagate": True}},
}

LOGGING["handlers"]["console"] = {"level": "DEBUG", "class": "logging.StreamHandler", "stream": sys.stdout}

LOGGING["loggers"][""] = {"handlers": ["console"], "level": "DEBUG"}

# SENTRY CONFIG
LOW_SAMPLE_RATE_TRANSACTIONS = ["/ping.json", "/healthcheck.json"]


def traces_sampler(sampling_context):
    try:
        name = sampling_context["wsgi_environ"].get("PATH_INFO")
    except Exception:
        pass
    else:
        if name in LOW_SAMPLE_RATE_TRANSACTIONS:
            return 0.0001
    return 0.1


if "SENTRY_DSN" in os.environ:
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        integrations=[DjangoIntegration()],
        traces_sampler=traces_sampler,
        environment=os.environ.get("ENV", "unknown"),
    )

TEST_RUNNER = "xmlrunner.extra.djangotestrunner.XMLTestRunner"
TEST_OUTPUT_DIR = "test-reports"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# .local.py overrides all the common settings.
try:
    from laalaa.settings.local import *  # noqa: F401,F403
except ImportError:
    pass


def override_setting(arg):
    prefix = "--override-setting="
    if arg and arg.startswith(prefix):
        exec(arg[len(prefix) :])
        return arg


if not hasattr(sys, "cli_args_overrides"):

    def remove_arg(arg):
        return sys.argv.remove(arg)

    map(remove_arg, filter(None, map(override_setting, sys.argv)))
    setattr(sys, "cli_args_overrides", True)
