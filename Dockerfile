FROM ghcr.io/osgeo/gdal:alpine-small-3.9.0

RUN apk upgrade --no-cache && \
    apk add --no-cache \
      bash \
      postgresql-client \
      tzdata

RUN adduser -D app && \
    cp /usr/share/zoneinfo/Europe/London /etc/localtime

# To install pip dependencies
RUN apk add --no-cache \
      build-base \
      linux-headers \
      postgresql-dev \
      curl-dev \
      python3-dev \
      geos-dev \
      py-pip

WORKDIR /home/app

COPY requirements/base.txt requirements/base.txt

COPY . .

RUN chown -R app:app laalaa/tmp
RUN mkdir laalaa/static
RUN chown -R app:app laalaa/static

USER 1000
RUN pip install --user --break-system-packages -r ./requirements/base.txt

# Kubernetes deploy does not need this as it runs it in a Job with the s3 storage backend set,
# so it can be removed once we're fully migrated
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["docker/run.sh"]
