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
export UWSGI_CONFIG_FILE=${UWSGI_CONFIG_FILE:-/home/app/conf/uwsgi.ini:allinone}  # Until we move off template deploy and onto Kubernetes with the split app
export WORKER_APP_CONCURRENCY=${WORKER_APP_CONCURRENCY:-8}
/usr/bin/uwsgi --ini $UWSGI_CONFIG_FILE
