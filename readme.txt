in django/ - docker build -t laalaa_django .
in postgres/ - docker build -t laalaa_db .

docker-compose run --service-ports django /bin/bash

in django container:

./runonce.sh
./runserver.sh