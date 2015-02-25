#!/bin/bash

gosu postgres postgres --single <<- EOSQL
    CREATE DATABASE laa_legal_adviser_api -E UTF8;
    CREATE EXTENSION postgis;
EOSQL
