#!/bin/sh
set +e

IFS=$(printf '\n\t')

# Docker
sudo apt-get update

if ! docker -v >/dev/null; then
  yes | sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --batch --yes --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo \
    "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
  sudo apt-get update
  yes | sudo apt-get install docker-ce docker-ce-cli containerd.io
  sudo usermod -aG docker $USER
  newgrp docker
  sudo systemctl start docker
  sudo systemctl enable docker
  printf '\nDocker installed and started successfully\n\n'
else
  printf "Docker is already exists!\n"
fi

# Docker Compose
if ! docker-compose -v >/dev/null; then
  sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  printf '\nDocker Compose installed successfully\n\n'
else
  printf "Docker Compose is already exists!"
fi
