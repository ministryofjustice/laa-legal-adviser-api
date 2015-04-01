FROM ubuntu:trusty

RUN echo "Europe/London" > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata

RUN apt-get update && \
    apt-get install -y software-properties-common python-software-properties

RUN apt-get update && \
    apt-get install -y \
        build-essential git python python-dev python-setuptools python-pip \
        supervisor curl libpq-dev ntp libproj-dev binutils gdal-bin \
        postgis postgresql-9.3-postgis-scripts vim

RUN mkdir /var/log/uwsgi && chown -R www-data:www-data /var/log/uwsgi

# fix for broken pip package in ubuntu 14
RUN easy_install -U pip

WORKDIR /app

ADD ./conf/uwsgi /etc/uwsgi

ADD ./conf/supervisor /etc/supervisor

ADD ./requirements.txt /app/requirements.txt
ADD ./requirements /app/requirements
RUN pip install -r requirements.txt

ADD . /app

EXPOSE 80
EXPOSE 8000
CMD ["supervisord", "-n"]
