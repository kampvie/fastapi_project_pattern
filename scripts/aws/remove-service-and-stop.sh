#!/bin/bash
set +e

cd /usr/app/{{PROJECT_NAME}} || exit
source ./project.settings
# Docker management
docker volume prune
docker system prune
docker-compose down
# Service management
if [ -e /etc/systemd/system/$SERVICE_NAME.service ]; then
    sudo systemctl stop $SERVICE_NAME.service
    sudo systemctl disable $SERVICE_NAME.service
    sudo rm /etc/systemd/system/$SERVICE_NAME.service
fi
# Remove code folder if existed!
if [ -d /usr/app/{{PROJECT_NAME}} ]; then
    sudo rm -rf /usr/app/{{PROJECT_NAME}}
fi