#!/usr/bin/env bash
set -e
exec ./manage.py ping_db
exec celery -A laalaa status
