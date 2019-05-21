#!/bin/sh -xe
kubectl config use-context docker-for-desktop
ECR_DEPLOY_IMAGE=laalaa_local .circleci/deploy_to_kubernetes development