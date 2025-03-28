#!/bin/bash

git pull
set -a
source .env-min
set +a

# For 4G deployment only
docker compose -f 4g-volte-min.yaml build --no-cache pyhss
docker compose -f 4g-volte-min.yaml rm -f pyhss
docker compose -f 4g-volte-min.yaml up -d --force-recreate pyhss