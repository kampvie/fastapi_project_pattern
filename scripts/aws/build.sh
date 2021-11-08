#!/bin/bash
set +e
cd /usr/app/{{PROJECT_NAME}} || exit
source ./project.settings
docker-compose build
yes | docker image prune
