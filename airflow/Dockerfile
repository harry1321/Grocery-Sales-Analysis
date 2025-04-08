# Dockerfile for Apache Airflow
FROM apache/airflow:2.10.5

# Copy the necessary files
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
