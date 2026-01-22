#!/usr/bin/env bash
set -e

# Create POSTGIS extensions if they do not exist
bash /home/app/docker/setup_postgres.sh

# Run migrations if there are any
./manage.py migrate

if [ "$ENV" != "prod" ]; then
  echo "$ENV: Seeding data"
  ./manage.py seed
fi
if [ "$ENV" == "local" ]; then
  echo "$ENV: running dev server"
  python manage.py runserver 0.0.0.0:8000
else
  echo "$ENV: running server"
  export WORKER_APP_CONCURRENCY=${WORKER_APP_CONCURRENCY:-8}
  /home/app/.local/bin/uwsgi --ini /home/app/conf/uwsgi.ini
fi
