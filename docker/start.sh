#!/bin/bash -e
chown -R www-data:www-data /var/log/wsgi
PGPASSWORD=$POSTGRES_PASSWORD /usr/bin/psql laalaa -c 'CREATE EXTENSION IF NOT EXISTS postgis;' -U $POSTGRES_USER -h $POSTGRES_HOST
PGPASSWORD=$POSTGRES_PASSWORD /usr/bin/psql laalaa -c 'CREATE EXTENSION IF NOT EXISTS postgis_topology;' -U $POSTGRES_USER -h $POSTGRES_HOST
/usr/local/bin/uwsgi --ini /etc/uwsgi/laalaa.ini
