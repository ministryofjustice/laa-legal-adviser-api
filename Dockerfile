#
# LAALAA Dockerfile all environments
#
FROM phusion/baseimage:0.9.16

MAINTAINER Stuart Munro <stuart.munro@digital.justice.gov.uk>

# Runtime User
RUN useradd -m -d /home/app app

# Set timezone
RUN echo "Europe/London" > /etc/timezone  &&  dpkg-reconfigure -f noninteractive tzdata

# Dependencies
RUN DEBIAN_FRONTEND='noninteractive' \
  apt-get update && \
  apt-get -y --force-yes install bash apt-utils build-essential git software-properties-common libpq-dev g++ make \
  libpcre3 libpcre3-dev libxslt-dev libxml2-dev wget libffi-dev postgis postgresql-9.3-postgis-scripts \
  ntp libproj-dev binutils gdal-bin

RUN apt-get clean

# Install latest python
ADD ./docker/install_python.sh /install_python.sh
RUN chmod 755 /install_python.sh
RUN /install_python.sh

# Add requirements to docker
ADD ./requirements/base.txt /requirements.txt
RUN pip install -r /requirements.txt

# Add project directory to docker
ADD . /home/app
RUN rm -rf /home/app/.git
RUN  chown -R app: /home/app

# Set correct environment variables.
ENV HOME /home/app
WORKDIR /home/app
ENV APP_HOME /home/app
USER app
EXPOSE 8000

ENV DB_NAME laalaa
ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD postgres
ENV POSTGRES_HOST db
ENV POSTGRES_PORT 5432

