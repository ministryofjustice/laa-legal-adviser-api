FROM osgeo/gdal:alpine-normal-v2.4.1

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
      postgresql-dev

# Install python3.7 from a later repository than the base image uses
RUN apk add --repository=http://dl-cdn.alpinelinux.org/alpine/v3.10/main python3-dev=3.7.5-r1 && \
    rm /usr/bin/python && \
        ln -s /usr/bin/python3 /usr/bin/python && \
        ln -s /usr/bin/pip3 /usr/bin/pip

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
