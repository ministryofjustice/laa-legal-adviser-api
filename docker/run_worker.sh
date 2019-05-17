#!/bin/sh -e
exec ./manage.py celery celery worker -A laalaa --concurrency=1 --loglevel=INFO
