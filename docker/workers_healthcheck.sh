#!/usr/bin/env bash
set -e
exec ./manage.py worker_health_checks
# This timeouts on the new cluster and there is no way to pass the --timeout option in this version of celery
# exec celery -A laalaa status
