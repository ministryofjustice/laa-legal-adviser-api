#!/usr/bin/env bash
set -e

# Create POSTGIS extensions f they do not exist
bash /home/app/docker/setup_postgres.sh

# Run migrations if there are any
./manage.py migrate

# Run server
/usr/local/bin/uwsgi --ini /home/app/conf/uwsgi.ini
