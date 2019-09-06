FROM alpine:3.10

RUN apk add --no-cache \
      bash \
      postgresql-client \
      py2-pip \
      tzdata && \
    apk add --no-cache \
      gdal \
      --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/

RUN adduser -D app && \
    cp /usr/share/zoneinfo/Europe/London /etc/localtime

# To install pip dependencies
RUN apk add --no-cache \
      build-base \
      linux-headers \
      postgresql-dev \
      python2-dev && \
    pip install -U setuptools pip==18.1 wheel

WORKDIR /home/app

COPY requirements/base.txt requirements/base.txt
RUN pip install -r ./requirements/base.txt

COPY . .

RUN python manage.py collectstatic --noinput

USER 1000
EXPOSE 8000

CMD ["docker/run.sh"]
