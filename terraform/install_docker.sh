#!/bin/bash

# 更新系統套件
echo "Updating package lists..."
sudo apt-get update

# 安裝必要套件
echo "Installing dependencies..."
sudo apt-get -y install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

# 加入 Docker 的官方 GPG 密鑰
echo "Adding Docker's official GPG key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# 設定 Docker 的穩定版本庫
echo "Adding Docker's repository..."
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

# 更新套件清單
echo "Updating package lists again after adding Docker repository..."
sudo apt-get update

# 安裝 Docker
echo "Installing Docker..."
sudo apt-get -y install docker-ce docker-ce-cli containerd.io

# 將當前使用者加入 Docker 群組
echo "Adding current user to docker group..."
sudo usermod -aG docker $(whoami)

# 使群組變更立即生效
echo "Applying group change..."
newgrp docker

# 下載 Docker Compose
echo "Downloading Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/1.25.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 設定 Docker Compose 可執行權限
echo "Setting executable permissions for Docker Compose..."
sudo chmod +x /usr/local/bin/docker-compose

# 完成安裝
echo "Docker and Docker Compose have been installed successfully."

git clone https://github.com/harry1321/Retail-Promo-Analysis.git
cd Retail-Promo-Analysis
mkdir -p ./dags ./logs ./plugins ./config
# PermissionError: [Errno 13] Permission denied: '/opt/airflow/logs/scheduler'
# 這表示 Airflow 嘗試建立 log 目錄 /opt/airflow/logs/scheduler 時失敗了
# 因為權限不足，導致 webserver 無法啟動成功。
sudo chown -R 50000:0 airflow/logs
