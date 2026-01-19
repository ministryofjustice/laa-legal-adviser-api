# LAA Legal Adviser API

[![Coverage Status](https://coveralls.io/repos/github/ministryofjustice/laa-legal-adviser-api/badge.svg?branch=master)](https://coveralls.io/github/ministryofjustice/laa-legal-adviser-api?branch=master)

Service to search for nearby LAA Legal Advisers by postcode.

The search is based on looking up latitude and longitude from the given postcode and finding legal advisers who are
near that point.

## Dependencies

* Virtualenv
* Python 3.11 (follow the [FALA installation guide](https://github.com/ministryofjustice/fala/blob/main/docs/virtual-env.md) and use `pyenv` to install correct version of python)
* Redis
* PostgreSQL => 14 (`pg_config`, `createdb` and `psql` commands available in the `PATH`)
* [PostGIS](https://postgis.net/) (`brew install postgis`)
  * Go get a hot beverage whilst waiting for this step to finish

    docker-compose run start_services

## Installation

"pyenv" is the tool we use to install and use the correct version of Python. (Other CLA repos need different python versions, and we've settled on pyenv as the best way to easily switch versions, depending on the repo you're in.)

1. Install pyenv with brew:

       brew install pyenv

2. Set up your shell for pyenv. Make the changes to `~/.zshrc` described here: [Set up your shell for pyenv](https://github.com/pyenv/pyenv#set-up-your-shell-environment-for-pyenv) (This is so that pyenv's python binary can be found in your path)

3. To make the shell changes take effect:

       . ~/.zshrc (or whatever your local shell file is e.g. .bashrc for bash)

   (or alternatively, restart your shell)

4. Install into pyenv the python version this repo uses (which is defined in `.python-version`):

       pyenv install 3.11
       pyenv local 3.11

```sh
python -m venv venv

# Start the virtualenv
source venv/bin/activate

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

## Git hooks

Repository uses [MoJ DevSecOps hooks](https://github.com/ministryofjustice/devsecops-hooks) to ensure `pre-commit` git hook is evaluated for series of checks before pushing the changes from staging area. Engineers should ensure `pre-commit` hook is configured and activated.

1. **Installation**:

   Ensure [prek](https://github.com/j178/prek?tab=readme-ov-file#installation) is installed globally

   Linux / MacOS

   ```bash
   curl --proto '=https' --tlsv1.2 -LsSf https://raw.githubusercontent.com/ministryofjustice/devsecops-hooks/e85ca6127808ef407bc1e8ff21efed0bbd32bb1a/prek/prek-installer.sh | sh
   ```

   or 

   ```bash
   brew install prek
   ```

   Windows

   ```bash
   powershell -ExecutionPolicy ByPass -c "irm https://raw.githubusercontent.com/ministryofjustice/devsecops-hooks/e85ca6127808ef407bc1e8ff21efed0bbd32bb1a/prek/prek-installer.ps1 | iex"
   ```

3. **Activation**

   Execute the following command in the repository directory

   ```bash
   prek install
   ```

4. **Test**

    To dry-run the hook

   ```bash
   prek run
   ```

## 🔧 Configuration

### Exclusion list

One can exclude files and directories by adding them to `exclude` property. Exclude property accepts [regular expression](https://pre-commit.com/#regular-expressions).

Ignore everything under `reports` and `docs` directories for `baseline` hook as an example.

```yaml
   repos:
     - repo: https://github.com/ministryofjustice/devsecops-hooks
       rev: v1.0.0
       hooks:
         - id: baseline
            exclude: |
            ^reports/|
            ^docs/
```

Or one can also create a file with list of exclusions.

```yaml
repos:
  - repo: https://github.com/ministryofjustice/devsecops-hooks
    rev: v1.0.0
    hooks:
      - id: baseline
        exclude: .pre-commit-ignore
```
