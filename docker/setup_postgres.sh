#!/usr/bin/env bash

/usr/bin/psql "${DATABASE_URL/postgis/postgres}" -c 'CREATE EXTENSION IF NOT EXISTS postgis;'
/usr/bin/psql "${DATABASE_URL/postgis/postgres}" -c 'CREATE EXTENSION IF NOT EXISTS postgis_topology;'
