# Dockerfile for Apache Airflow
FROM apache/airflow:2.10.5-python3.12

# Install additional dependencies
USER root
RUN apt-get update && apt-get install -y \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Set permissions
USER airflow

# Expose Web UI port
EXPOSE 8080

CMD ["airflow", "standalone"]