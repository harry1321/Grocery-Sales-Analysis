# Dockerfile for Apache Airflow
FROM apache/airflow:2.8.4

# Copy the necessary files
COPY ./airflow/requirements.txt ${AIRFLOW_HOME}/requirements.txt
RUN pip install --no-cache-dir -r ${AIRFLOW_HOME}/requirements.txt
