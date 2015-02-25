FROM postgres:9.4
ADD create-database.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/create-database.sh
