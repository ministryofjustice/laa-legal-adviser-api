!#/bin/bash

PGPASSWORD=$POSTGRES_PASSWORD /usr/bin/psql --host $POSTGRES_HOST -U $POSTGRES_USER $POSTGRES_USER -f ./docker/sql/create_db.sql
PGPASSWORD=$POSTGRES_PASSWORD /usr/bin/psql --host $POSTGRES_HOST -d laalaa -U $POSTGRES_USER $POSTGRES_USER -f ./docker/sql/create_extensions.sql
python /home/app/manage.py migrate
python /home/app/manage.py createsuperuser --username=admin