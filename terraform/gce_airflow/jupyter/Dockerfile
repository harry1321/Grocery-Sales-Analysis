# Dockerfile for Jupyter Notebook
FROM jupyter/pyspark-notebook:latest
FROM jupyter/base-notebook:python-3.9

# Install additional dependencies

USER root
RUN apt-get update && apt-get install -y \
    vim \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r /requirements.txt

USER jovyan
WORKDIR /home/jovyan

# Expose Jupyter Notebook port
EXPOSE 8888

CMD ["start-notebook.sh", "--NotebookApp.password=${JUPYTER_PASSWORD}"]