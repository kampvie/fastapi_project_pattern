#!/bin/bash

# Export all enviroment variables to use later
source ../../project.settings
# Change working directory to home
cd $HOME
# Pull project from VCS
if [[ -d "$PROJECT_NAME" ]]; then
  cd $PROJECT_NAME || exit
  git pull
else
  yes | git clone $GIT_SSH_REPO
  cd $PROJECT_NAME || exit
fi
chmod 555 ./entrypoint.sh
# Docker management
docker-compose down
docker-compose build
yes | docker image prune
# Service management
sudo systemctl stop $SERVICE_NAME.service
sudo systemctl disable $SERVICE_NAME.service
sudo rm /etc/systemd/system/$SERVICE_NAME.service
# Create service file
SERVICE_FILE_PATH=$HOME/$SERVICE_NAME.service
echo "[Unit]" >$SERVICE_FILE_PATH
echo "Description=Start project $PROJECT_NAME service" >>$SERVICE_FILE_PATH
echo "After=network.target" >>$SERVICE_FILE_PATH
echo "[Service]" >>$SERVICE_FILE_PATH
echo "WorkingDirectory=$(pwd)" >>$SERVICE_FILE_PATH
echo "ExecStart=$(find /usr/ -name "docker-compose") up" >>$SERVICE_FILE_PATH
echo "Restart=on-failure" >>$SERVICE_FILE_PATH
echo "StandardOutput=syslog" >>$SERVICE_FILE_PATH
echo "StandardError=syslog" >>$SERVICE_FILE_PATH
echo "[Install]" >>$SERVICE_FILE_PATH
echo "WantedBy=multi-user.target" >>$SERVICE_FILE_PATH
#Copying service file to /ets/systemd/system
sudo cp $SERVICE_FILE_PATH /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start $SERVICE_NAME.service
sudo systemctl enable $SERVICE_NAME.service
