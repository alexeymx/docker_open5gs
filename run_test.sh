#!/bin/bash

set -a
source .env
set +a
sudo ufw disable
sudo sysctl -w net.ipv4.ip_forward=1
sudo cpupower frequency-set -g performance

# For 4G deployment only
docker-compose -f srsenb_zmq.yaml build
docker-compose -f srsenb_zmq.yaml up -d
