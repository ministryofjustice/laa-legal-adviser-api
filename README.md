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

As a convenience, a `docker-compose.yml` specifies these dependendencies and can be run with:

    docker-compose run start_services

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

Create a local.py settings file from the example file:

```
cp laalaa/settings/local.py.example laalaa/settings/local.py
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

## Releasing

### Releasing to non-production

> Currently, `staging` is the only non-production environment.

1. Wait for [the Docker build to complete on CircleCI](https://circleci.com/gh/ministryofjustice/laa-legal-adviser-api) for the feature branch.
1. Copy the `feature_branch.<sha>` reference from the `build` job's "Push Docker image" step. Eg:
    ```
    Pushing tag for rev [1ad776954b2e] on {https://registry.service.dsd.io/v1/repositories/laalaa/tags/dependabot-pip-django-filter-2.0.0.7243223}}
    ```
1. [Deploy `feature_branch.<sha>`](https://ci.service.dsd.io/view/LaaLaa/job/DEPLOY-laalaa/build?delay=0sec).
    * `ENVIRONMENT` is the target environment, select "staging".
    * `DEPLOY_BRANCH` is the [deploy repo's](https://github.com/ministryofjustice/laalaa-deploy) default branch name, usually master.
    * `VERSION` is the branch that needs to be released plus a specific 7-character prefix of the Git SHA. (`dependabot-pip-django-filter-2.0.0.7243223` for the above example).

### Releasing to production

1. Please make sure you tested on a non-production environment before merging.
1. Merge your feature branch pull request to `master`.
1. Wait for [the Docker build to complete on CircleCI](https://circleci.com/gh/ministryofjustice/laa-legal-adviser-api/tree/master) for the `master` branch.
1. Copy the `master.<sha>` reference from the `build` job's "Tag and push Docker images" step. Eg:
    ```
    Pushing tag for rev [70079f727578] on {https://registry.service.dsd.io/v1/repositories/laalaa/tags/master.9d39b80}
    ```
1. [Deploy `master.<sha>` to **prod**uction](https://ci.service.dsd.io/view/LaaLaa/job/DEPLOY-laalaa/build?delay=0sec).

:tada: :shipit:
