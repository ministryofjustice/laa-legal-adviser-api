#!/usr/bin/env bash

PGPASSWORD=$DB_PASSWORD /usr/bin/psql --host $DB_HOST -U $DB_USERNAME $DB_NAME -c 'CREATE EXTENSION IF NOT EXISTS postgis;'
PGPASSWORD=$DB_PASSWORD /usr/bin/psql --host $DB_HOST -U $DB_USERNAME $DB_NAME -c 'CREATE EXTENSION IF NOT EXISTS postgis_topology;'
