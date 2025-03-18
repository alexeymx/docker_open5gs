#!/bin/bash

git pull
set -a
source .env-min
set +a
sudo ufw disable
sudo sysctl -w net.ipv4.ip_forward=1
sudo cpupower frequency-set -g performance

# For 4G deployment only
docker compose -f 4g-volte-min.yaml build
docker compose -f 4g-volte-min.yaml up -d
