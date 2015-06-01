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

here = lambda *x: join(abspath(dirname(__file__)), *x)
PROJECT_ROOT = here("..")
root = lambda *x: join(abspath(PROJECT_ROOT), *x)

sys.path.insert(0, root('apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'DEV_KEY')

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',

    'rest_framework',

    'advisers'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'laalaa.urls'

WSGI_APPLICATION = 'laalaa.wsgi.application'

TEMPLATE_DIRS = (
    root('templates'),
)

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('DB_USERNAME', 'laalaa'),
        'USER': os.environ.get('DB_USERNAME', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = root('uploads',)
MEDIA_URL = '/uploads/'
# 10MB
MAX_UPLOAD_SIZE = 10485760
# Force uploaded files to be written to disk
FILE_UPLOAD_MAX_MEMORY_SIZE = 0

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = root('static')

REST_FRAMEWORK = {
    'PAGINATE_BY': 10,
    'EXCEPTION_HANDLER': 'advisers.views.custom_exception_handler'
}

ADDRESSFINDER_API_HOST = os.environ.get(
    'ADDRESSFINDER_API_HOST',
    'http://127.0.0.1:8003')
ADDRESSFINDER_API_TOKEN = os.environ.get('ADDRESSFINDER_API_TOKEN', '')

# .local.py overrides all the common settings.
try:
    from .local import *
except ImportError:
    pass

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'logstash': {
            '()': 'logstash_formatter.LogstashFormatter'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        }
    }
}

#APP LOGGING CONFIG
LOGGING['handlers']['production_file'] = {
    'level' : 'INFO',
    'class' : 'logging.handlers.RotatingFileHandler',
    'filename' : 'app.log',
    'maxBytes': 1024*1024*5, # 5 MB
    'backupCount' : 7,
    'formatter': 'logstash',
    'filters': ['require_debug_false'],
}

LOGGING['handlers']['debug_file'] = {
    'level' : 'DEBUG',
    'class' : 'logging.handlers.RotatingFileHandler',
    'filename' : 'debug.log',
    'maxBytes': 1024*1024*5, # 5 MB
    'backupCount' : 7,
    'formatter': 'logstash',
    'filters': ['require_debug_true'],
}

LOGGING['handlers']['console'] = {
   'level': 'DEBUG',
   'class': 'logging.StreamHandler',
   'stream': sys.stdout
}

LOGGING['loggers'][''] = {
    'handlers': ['console'],
    'level': "DEBUG",
}

# RAVEN SENTRY CONFIG
if 'SENTRY_DSN' in os.environ:
    RAVEN_CONFIG = {
        'dsn': os.environ.get('SENTRY_DSN')
    }

    INSTALLED_APPS += (
        'raven.contrib.django.raven_compat',
    )

    MIDDLEWARE_CLASSES = (
        'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
    ) + MIDDLEWARE_CLASSES


def override_setting(arg):
    prefix = '--override-setting='
    if arg and arg.startswith(prefix):
        exec(arg[len(prefix):])
        return arg


if not hasattr(sys, 'cli_args_overrides'):
    remove_arg = lambda arg: sys.argv.remove(arg)
    map(remove_arg, filter(None, map(override_setting, sys.argv)))
    setattr(sys, 'cli_args_overrides', True)
