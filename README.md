LAA Legal Adviser API
=====================

Service to search for LAA Legal Advisers by lat/lon.

Dependencies
------------

* Virtualenv
* Python 2.7
* RabbitMQ
* PostgreSQL => 9.3 (`pg_config`, `createdb` and `psql` commands available in the `PATH`)
* [PostGIS](https://postgis.net/)

:memo: If you are using Docker to provide a database, please use `circleci/postgres:9.4-alpine-postgis`, which has the required extensions installed.

    docker run --detach --publish 5432:5432 circleci/postgres:9.4-alpine-postgis

:memo: If you are using Docker to provide RabbitMQ, it's preferable to use one with management interface enabled:

    docker run --detach --publish 5672:5672 --publish 15672:15672 rabbitmq:3.7-management-alpine

Installation
------------

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

# Create the database tables and populate with dummy data
# and create a Django admin account:
python manage.py migrate
python manage.py createsuperuser --username=admin

```

Each Run
--------

```sh
#Add the correct environment variable
export POSTCODEINFO_AUTH_TOKEN=auth-token-no-space-or-quotes 
```

...or add it to your `laalaa/settings/local.py` settings.

| Service | Command |
| --- | --- |
| API | `python manage.py runserver` |
| Worker | `python manage.py celery worker` |

There is a Django admin site which allows importing and editing the database of legal advisers.

Go to admin/ and sign in with the admin password you just set.


# Jenkins CI Build Jobs
The development build job and the development & prod deploy jenkins jobs are here http://jenkins.dsd.io/view/laalaa/

The docker image is built on a jenkins slave (cla-slave) and pushed to the docker registry - https://registry.service.dsd.io. If successful, a development deploy job is triggered on an EC2 instance. The prod deploy job is triggered manually. More information on the deployment is available here https://github.com/ministryofjustice/laalaa-deploy/blob/master/README.rst
