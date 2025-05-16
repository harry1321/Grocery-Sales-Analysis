#!/bin/bash

mkdir -p ~/spark
cd ~/spark
# install java
wget https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz
tar xzfv openjdk-11.0.2_linux-x64_bin.tar.gz
rm openjdk-11.0.2_linux-x64_bin.tar.gz
echo 'export JAVA_HOME=$HOME/spark/jdk-11.0.2' >> ~/.bashrc
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
# install spark
# find the version you want from https://spark.apache.org/downloads.html
# using version 3.3.2
wget https://archive.apache.org/dist/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz
tar xzfv spark-3.3.2-bin-hadoop3.tgz
rm spark-3.3.2-bin-hadoop3.tgz
echo 'export SPARK_HOME=~/spark/spark-3.3.2-bin-hadoop3' >> ~/.bashrc
echo 'export PATH=$SPARK_HOME/bin:$PATH' >> ~/.bashrc

# for pyspark
echo 'export PYTHONPATH=$SPARK_HOME/python/:$PYTHONPATH' >> ~/.bashrc
echo 'export PYTHONPATH=$SPARK_HOME/python/lib/py4j-0.10.9.7-src.zip:$PYTHONPATH' >> ~/.bashrc

source ~/.bashrc

cd ..

echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y maven unzip python3-pip git
sudo apt-get install -y python-is-python3 || true

# install python packages
pip install --upgrade pip
pip install scikit-learn yellowbrick seaborn matplotlib pandas jupyter

# install Livy API for Airflow
git clone https://github.com/apache/incubator-livy.git
cd incubator-livy
# mvn clean package -B -V -e -Pspark-3 -Pscala-2.12 -Pthriftserver -DskipTests -DskipITs -Dmaven.javadoc.skip=true
# 若出現錯誤使用下面指令
mvn clean package -DskipTests

# edit Livy conf
cd ~/livy/conf
cp livy.conf.template livy.conf
cat <<EOF >> livy.conf
livy.server.session.timeout=1h
livy.server.recovery.mode=off
livy.spark.master=local[*]
livy.spark.deploy-mode=client
livy.environment=production
livy.file.local-dir-whitelist=$HOME/spark
EOF

cd ~/spark
git clone https://github.com/harry1321/Grocery-Sales-Analysis.git

# activate Livy API
cd ~/livy/bin
./livy-server start