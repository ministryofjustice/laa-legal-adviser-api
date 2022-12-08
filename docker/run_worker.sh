#!/usr/bin/env bash
set -e
exec celery -A laalaa worker --concurrency=${WORKER_APP_CONCURRENCY:-4} --loglevel=${LOG_LEVEL:-INFO}
