# LAA Legal Adviser API

Service to search for nearby LAA Legal Advisers by postcode.

The search is based on looking up latitude and longitude from the given postcode and finding legal advisers who are
near that point.

## Dependencies

* Virtualenv
* Python 2.7
* RabbitMQ
* PostgreSQL => 9.3 (`pg_config`, `createdb` and `psql` commands available in the `PATH`)
* [PostGIS](https://postgis.net/) (`brew install postgis`)

:memo: If you are using Docker to provide a database, please use `circleci/postgres:9.4-alpine-postgis`, which has the required extensions installed.

    docker run --detach --publish 5432:5432 circleci/postgres:9.4-alpine-postgis

:memo: If you are using Docker to provide RabbitMQ, it's preferable to use one with management interface enabled:

    docker run --detach --publish 5672:5672 --publish 15672:15672 rabbitmq:3.7-management-alpine

## Installation

```sh
# Install Virtualenv if necessary
# sudo may be required if Python is not installed via brew
pip install virtualenv

# Create a virtualenv
# In the directory in which the virtualenv directory should be created
virtualenv -p python2 venv

# Start the virtualenv
source venv/bin/activate

# Install further requirements with pip, assuming you are in the
# project directory
pip install -r requirements/development.txt

# Create a database and install required PostgreSQL extensions
PGHOST=localhost PGUSER=postgres ./setup_postgres.sh

# Create the database tables and create a Django admin account:
python manage.py migrate
python manage.py createsuperuser --username=admin
```

To populate the database with initial seed data, run:
```
python manage.py seed
```

## Running the services

| Service | Command |
| --- | --- |
| API | `python manage.py runserver` |
| Worker | `python manage.py celery worker` |

There is a Django admin site which allows importing and editing the database of legal advisers.

Go to admin/ and sign in with the admin password you just set.

## Building and deployment

The repository unit tests and Docker images are built by CircleCI at https://circleci.com/gh/ministryofjustice/laa-legal-adviser-api.

Deployment can be triggered via https://ci.service.dsd.io/job/DEPLOY-laalaa.
