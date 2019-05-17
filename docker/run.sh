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
APP_NAME=${APP_NAME:-allinone}  # Until we move off template deploy and onto Kubernetes with the split app
WORKER_APP_CONCURRENCY = ${WORKER_APP_CONCURRENCY:-8}
/usr/local/bin/uwsgi --ini /home/app/conf/uwsgi.ini:$APP_NAME
