#
# LAALAA Dockerfile all environments
#
FROM phusion/baseimage:0.9.16

MAINTAINER Stuart Munro <stuart.munro@digital.justice.gov.uk>

# Runtime User
RUN useradd --uid 1000 --user-group -m -d /home/app app

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
RUN /install_python.sh

# Add requirements to docker
ADD ./requirements/base.txt /requirements.txt
RUN pip install -r /requirements.txt

# Add project to container
ADD . /home/app

# Set correct environment variables.
ENV HOME /home/app
ENV APP_HOME /home/app
WORKDIR /home/app

RUN docker/collectstatic.sh

# Project permissions
RUN  chown -R app: /home/app

# Specify the user by numeric ID, for environments which use the ID to determine that the user is non-root
USER 1000
EXPOSE 8000

CMD ["/home/app/docker/run.sh"]
