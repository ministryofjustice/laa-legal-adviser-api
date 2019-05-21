#!/bin/sh -e
exec ./manage.py celery worker -A laalaa --concurrency=$WORKER_APP_CONCURRENCY --loglevel=$LOG_LEVEL
