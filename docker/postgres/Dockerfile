FROM mdillon/postgis:9.4
ADD create-database.sh /docker-entrypoint-initdb.d/zz_create_db.sh
RUN chmod +x /docker-entrypoint-initdb.d/zz_create_db.sh
