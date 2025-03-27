#!/bin/bash

# 設定變數
# USER_NAME=$(whoami)
# PROJECT_DIR="/home/$USER_NAME/project"

echo "==========> [$(date)] 開始執行 startup_script.sh" | tee /dev/ttyS1

# 更新系統並安裝 Docker & Docker Compose
echo "[$(date)] 更新系統..." | tee /dev/ttyS1
sudo apt-get update -y

echo "==========> [$(date)] 安裝 Docker & Docker Compose..." | tee /dev/ttyS1
sudo apt-get install -y docker.io docker-compose

# 啟動 Docker 服務
echo "==========> [$(date)] 啟動 Docker 服務..." | tee /dev/ttyS1
sudo systemctl start docker
sudo systemctl enable docker

# 將目前的使用者加入 docker 群組（避免用 root 運行）
# echo "==========> [$(date)] 將 $USER_NAME 加入 docker 群組..." | tee /dev/ttyS1
# sudo usermod -aG docker $USER_NAME
# newgrp docker  # 立即套用群組變更

# 下載專案檔案（假設你有 Git 存儲庫）
# echo "==========> [$(date)] 下載專案到 $PROJECT_DIR..." | tee /dev/ttyS1
# git clone https://your-repo-url.git $PROJECT_DIR

# if [ $? -ne 0 ]; then
#     echo "[$(date)] Git clone 失敗，可能已經存在" | tee /dev/ttyS1
# else
#     echo "[$(date)] Git clone 成功" | tee /dev/ttyS1
# fi

# cd $PROJECT_DIR

# 確保資料夾存在，並賦予正確權限
echo "==========> [$(date)] 建立資料夾並設定權限..." | tee /dev/ttyS1
mkdir -p airflow_data jupyter_data
chown -R $USER_NAME:$USER_NAME airflow_data jupyter_data

# 測試 Docker 是否可用
echo "==========> [$(date)] 測試 Docker 是否安裝成功..." | tee /dev/ttyS1
docker --version | tee /dev/ttyS1
docker-compose --version | tee /dev/ttyS1

# 啟動容器
# echo "[$(date)] 啟動 Docker 容器..." | tee /dev/ttyS1
# docker-compose up -d

# if [ $? -ne 0 ]; then
#     echo "[$(date)] Docker Compose 啟動失敗！請檢查錯誤訊息" | tee /dev/ttyS1
# else
#     echo "[$(date)] Docker Compose 啟動成功！" | tee /dev/ttyS1
# fi

echo "[$(date)] 啟動腳本執行完成！" | tee /dev/ttyS1
