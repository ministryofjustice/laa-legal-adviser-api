#!/bin/bash -ex

DOCKER_REGISTRY='registry.service.dsd.io'
APP_NAME='laalaa'
DOCKER='docker'
(( EUID == 0 )) || DOCKER='sudo docker'

[[ $(curl -o /dev/null --silent --head --write-out '%{http_code}\n' https://$DOCKER_REGISTRY/v1/repositories/$APP_NAME/images) == '200' ]] || { echo -e "\nTHE DOCKER REGISTRY IS DOWN!"; exit 1; }

DOCKER build --force-rm=true -t $DOCKER_REGISTRY/$APP_NAME .
DOCKER tag $DOCKER_REGISTRY/$APP_NAME $DOCKER_REGISTRY/$APP_NAME:$GIT_COMMIT
DOCKER push $DOCKER_REGISTRY/$APP_NAME
