#!/usr/bin/env bash
set -e
exec ./manage.py worker_health_checks
exec celery -A laalaa status
