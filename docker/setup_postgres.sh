#!/usr/bin/env bash

DB_NAME=${DB_NAME:-$DB_USERNAME}  # Until we move off template deploy and onto Kubernetes with the new DB

PGPASSWORD=$DB_PASSWORD /usr/bin/psql --host $DB_HOST -U $DB_USERNAME $DB_NAME -c 'CREATE EXTENSION IF NOT EXISTS postgis;'
PGPASSWORD=$DB_PASSWORD /usr/bin/psql --host $DB_HOST -U $DB_USERNAME $DB_NAME -c 'CREATE EXTENSION IF NOT EXISTS postgis_topology;'
