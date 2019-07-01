#!/usr/bin/env bash
set -e
exec ./manage.py ping
exec celery -A laalaa status
