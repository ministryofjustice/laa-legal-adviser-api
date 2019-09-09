#!/usr/bin/env bash
set -e
database="laalaa"
psql $database --command='SELECT 1' >/dev/null 2>/dev/null || createdb --echo "$database"
psql $database --command='CREATE EXTENSION IF NOT EXISTS postgis;'
psql $database --command='CREATE EXTENSION IF NOT EXISTS postgis_topology;'
