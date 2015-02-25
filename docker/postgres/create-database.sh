#!/bin/bash

echo "Create laa_legal_adviser_api database"
gosu postgres postgres --single <<- EOSQL
    CREATE DATABASE laa_legal_adviser_api TEMPLATE template_postgis;
EOSQL
