#!/usr/bin/env bash
set -e

# Create POSTGIS extensions f they do not exist
bash /home/app/docker/setup_postgres.sh

# Run migrations if there are any
./manage.py migrate

# Export host IP to container
#export RABBITMQ_SERVER=$(ip route get 8.8.8.8 | grep -oP 'via \K\S+')

# Run server
/usr/local/bin/uwsgi --ini /home/app/conf/uwsgi.ini
