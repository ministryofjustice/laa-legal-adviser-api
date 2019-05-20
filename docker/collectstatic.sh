#!/usr/bin/env bash

cd /home/app
python manage.py collectstatic --settings=laalaa.settings.no_db_docker_build --noinput
