#!/usr/bin/env bash
set -e

# Create POSTGIS extensions if they do not exist
bash /home/app/docker/setup_postgres.sh

# Run migrations if there are any
./manage.py migrate

if [ "$ENV" != "prod" ]; then
  ./manage.py seed
fi

# Run server
/usr/local/bin/uwsgi --ini /home/app/conf/uwsgi.ini
