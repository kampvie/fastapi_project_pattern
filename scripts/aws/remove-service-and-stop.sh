#!/bin/bash
set +e

cd /usr/app/{{PROJECT_NAME}} || exit
source ./project.settings
# Docker management
docker-compose down
# Service management
sudo systemctl stop $SERVICE_NAME.service
sudo systemctl disable $SERVICE_NAME.service
sudo rm /etc/systemd/system/$SERVICE_NAME.service
