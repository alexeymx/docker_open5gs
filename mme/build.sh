#!/bin/bash

set -a
source .env
set +a

git pull

# Variables
PROJECT_ID="v3-vinoc"
REGION="us-central1"
IMAGE_PATH="us-central1-docker.pkg.dev/$PROJECT_ID/epc-core"
TAG="latest"
YAML_ENV=$1 # Pass 'prod' or 'dev' as an argument

# Set namespace and container names based on the environment
if [ "$YAML_ENV" == "prod" ]; then
  NAMESPACE="epc-prod"
  CONTAINER_NAME="mme-prod"
elif [ "$YAML_ENV" == "dev" ]; then
  NAMESPACE="epc-dev"
  CONTAINER_NAME="mme-dev"
else
  echo "Invalid environment. Please specify 'prod' or 'dev'."
  exit 1
fi


gcloud auth activate-service-account --key-file=../../service-account.json
gcloud auth configure-docker us-central1-docker.pkg.dev

docker build --no-cache --force-rm -t $IMAGE_PATH/$CONTAINER_NAME:$TAG .
docker push $IMAGE_PATH/$CONTAINER_NAME:$TAG


echo "Pushed MME image: $IMAGE_PATH/$CONTAINER_NAME:$TAG"
