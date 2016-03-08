#!/bin/bash
docker run -d --volume="/home/docker/data:/var/lib/postgresql/data" --name="db_server" laalaa_db postgres