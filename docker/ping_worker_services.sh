#!/usr/bin/env bash
set -e
exec ./manage.py ping_db
exec ./manage.py ping_queue_workers
