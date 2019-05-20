#!/bin/sh -e
exec ./manage.py celery celery worker -A laalaa --concurrency=$WORKER_APP_CONCURRENCY --loglevel=INFO
