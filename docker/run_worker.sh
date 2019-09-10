#!/usr/bin/env bash
set -e
exec celery worker -A laalaa --concurrency=$WORKER_APP_CONCURRENCY --loglevel=$LOG_LEVEL
