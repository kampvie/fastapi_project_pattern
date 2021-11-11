#!/bin/bash
set +e
cd /usr/app/{{PROJECT_NAME}} || exit
source ./project.settings
# Create service file
SERVICE_FILE_PATH=/usr/app/{{PROJECT_NAME}}/$SERVICE_NAME.service
echo "[Unit]" >$SERVICE_FILE_PATH
echo "Description=Start {{PROJECT_NAME}} service" >>$SERVICE_FILE_PATH
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
if [ ! -e /etc/systemd/system/$SERVICE_NAME.service ]; then
    sudo cp $SERVICE_FILE_PATH /etc/systemd/system/
    sudo systemctl start $SERVICE_NAME.service
    sudo systemctl enable $SERVICE_NAME.service
else
    sudo systemctl restart $SERVICE_NAME.service
fi
