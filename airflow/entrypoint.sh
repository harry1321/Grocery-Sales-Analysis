#!/bin/bash

# Upgrade the database to ensure it's up-to-date
airflow db upgrade

# Check if the user already exists, if not, create it
airflow users list | grep -q "$AIRFLOW_USERNAME" || airflow users create \
    --username "$AIRFLOW_USERNAME" \
    --password "$AIRFLOW_PASSWORD" \
    --firstname "$AIRFLOW_FIRSTNAME" \
    --lastname "$AIRFLOW_LASTNAME" \
    --role "$AIRFLOW_ROLE" \
    --email "$AIRFLOW_EMAIL"

# Start webserver in the background & scheduler in the foreground
airflow webserver & airflow scheduler
