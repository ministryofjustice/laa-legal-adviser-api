# LAA Legal Adviser API

Service to search for nearby LAA Legal Advisers by postcode.

The search is based on looking up latitude and longitude from the given postcode and finding legal advisers who are
near that point.

## Dependencies

* Virtualenv
* Python 3.7
* Redis
* PostgreSQL => 9.3 (`pg_config`, `createdb` and `psql` commands available in the `PATH`)
* [PostGIS](https://postgis.net/) (`brew install postgis`)

:memo: If you are using Docker to provide a database, please use `circleci/postgres:9.4-alpine-postgis`, which has the required extensions installed.

    docker run --detach --publish 5432:5432 circleci/postgres:9.4-alpine-postgis

:memo: If you are using Docker to provide RabbitMQ, it's preferable to use one with management interface enabled:

    docker run --detach --publish 6379:6379 redis:4-alpine

As a convenience, a `docker-compose.yml` specifies these dependendencies and can be run with:

    docker-compose run start_services

## Installation

```sh
# Install Virtualenv if necessary
# sudo may be required if Python is not installed via brew
pip install virtualenv

# Create a virtualenv
# In the directory in which the virtualenv directory should be created
virtualenv -p python3 env

# Start the virtualenv
source env/bin/activate

# Install further requirements with pip, assuming you are in the
# project directory
pip install -r requirements/dev.txt

# Create a database and install required PostgreSQL extensions
PGHOST=localhost PGUSER=postgres ./setup_postgres.sh

# Create the database tables and create a Django admin account:
python manage.py migrate
python manage.py createsuperuser --username=admin
```

Postgres.app is a standalone PostgreSQL server that includes the PostGIS extension. You will also need to install gdal and libgeoip with Homebrew:
```
brew install postgis
brew install gdal
```
After installing Postgres.app, run this to add the following to your .bash_profile so you can run the package’s programs from the command-line: 
```
echo export PATH="/Applications/Postgres.app/Contents/Versions/9.4/bin:$PATH" >>~/.bash_profile
```

To populate the database with initial seed data, run:
```
python manage.py seed
```

Create a local.py settings file from the example file:

```
cp laalaa/settings/local.py.example laalaa/settings/local.py
```

## Categories
Although there is a category Django model, categories should not be managed / added by code.
Categories are remove and added as part of the providers spreadsheet upload which is done by
users. See https://github.com/ministryofjustice/laa-legal-adviser-api/pull/133

## Running the services

| Service | Command |
| --- | --- |
| API | `./manage.py runserver` |
| Worker | `celery worker` |

There is a Django admin site which allows importing and editing the database of legal advisers.

Go to admin/ and sign in with the admin password you just set.

## Lint and pre-commit hooks

To lint with Black and flake8, install pre-commit hooks:
```
. env/bin/activate
pip install -r requirements/dev.txt
pre-commit install
```

To run them manually:
```
pre-commit run --all-files
```

## Building and deployment

The repository unit tests and Docker images are built by CircleCI at https://circleci.com/gh/ministryofjustice/laa-legal-adviser-api.

Deployment can be triggered via https://ci.service.dsd.io/job/DEPLOY-laalaa.

## Releasing
* [Releasing](https://github.com/ministryofjustice/laa-civil-legal-aid-documentation/blob/master/releasing/kubernetes.md)
(opens in https://github.com/ministryofjustice/laa-civil-legal-aid-documentation)
