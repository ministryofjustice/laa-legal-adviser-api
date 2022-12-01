FROM osgeo/gdal:alpine-normal-3.6.0

RUN apk upgrade --no-cache && \
    apk add --no-cache \
    bash \
    postgresql-client \
    tzdata \
    py3-pip \
    python3-dev

RUN adduser -D app && \
    cp /usr/share/zoneinfo/Europe/London /etc/localtime

# To install pip dependencies
RUN apk add --no-cache \
    build-base \
    linux-headers \
    postgresql-dev

RUN pip install -U setuptools pip wheel

WORKDIR /home/app

COPY requirements/base.txt requirements/base.txt
RUN pip install -r ./requirements/base.txt

COPY . .

RUN chown -R app:app laalaa/tmp

# Kubernetes deploy does not need this as it runs it in a Job with the s3 storage backend set,
# so it can be removed once we're fully migrated
RUN python manage.py collectstatic --noinput

USER 1000
EXPOSE 8000

CMD ["docker/run.sh"]
