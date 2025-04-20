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
  O5G_CONTAINER_NAME="open5gs-core-prod"
  IMS_CONTAINER_NAME="ims-prod"
elif [ "$YAML_ENV" == "dev" ]; then
  NAMESPACE="epc-dev"
  O5G_CONTAINER_NAME="open5gs-core-dev"
  IMS_CONTAINER_NAME="ims-dev"
else
  echo "Invalid environment. Please specify 'prod' or 'dev'."
  exit 1
fi


gcloud auth activate-service-account --key-file=service-account.json
gcloud auth configure-docker us-central1-docker.pkg.dev

cd base

#docker build --no-cache --force-rm -t docker_open5gs .
docker build --no-cache --force-rm -t $IMAGE_PATH/$O5G_CONTAINER_NAME:$TAG .
docker push $IMAGE_PATH/$O5G_CONTAINER_NAME:$TAG


# Build docker images for kamailio IMS components
cd ../ims_base
#docker build --no-cache --force-rm -t docker_kamailio .
docker build --no-cache --force-rm -t $IMAGE_PATH/$IMS_CONTAINER_NAME:$TAG .
docker push $IMAGE_PATH/$IMS_CONTAINER_NAME:$TAG


echo "Pushed Open5GS image: $IMAGE_PATH/$O5G_CONTAINER_NAME:$TAG"
echo "Pushed Kamailio IMS image: $IMAGE_PATH/$IMS_CONTAINER_NAME:$TAG"