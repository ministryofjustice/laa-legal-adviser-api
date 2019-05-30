#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
NAMESPACE="development"
NAMESPACE_DIR="$ROOT/../kubernetes_deploy/$NAMESPACE"

kubectl config use-context docker-for-desktop

# Shared services deployment, only available for development to mock external services
kubectl apply --record=false --filename=$NAMESPACE_DIR/shared_services_deployment.yml

ECR_DEPLOY_IMAGE=laalaa_local .circleci/deploy_to_kubernetes $NAMESPACE
