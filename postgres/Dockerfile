#
# LAALAA Postgres
#
FROM postgres:9.4

# Set timezone
RUN echo "Europe/London" > /etc/timezone  &&  dpkg-reconfigure -f noninteractive tzdata

# Dependencies
RUN DEBIAN_FRONTEND='noninteractive' \
  apt-get update && \
  apt-get -y --force-yes install bash apt-utils postgis postgresql-9.4-postgis-scripts

RUN apt-get clean

ENV PG_USER postgres
ENV PG_PASSWORD postgres

EXPOSE 5432

#ENTRYPOINT ['/usr/lib/postgresql/9.4/bin/postgres']


