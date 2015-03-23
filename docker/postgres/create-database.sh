#!/bin/bash

echo "Create laalaa database"
gosu postgres postgres --single <<- EOSQL
    CREATE DATABASE laalaa TEMPLATE template_postgis;
EOSQL
