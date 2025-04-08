# Dockerfile for Apache Airflow
FROM apache/airflow

# Copy the necessary files
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
