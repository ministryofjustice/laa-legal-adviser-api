#!/bin/bash
docker run -Pit --volume="/home/docker/django:/home/app" --name="django_app" --expose 8123 --link="db_server:db" laalaa_django /bin/bash