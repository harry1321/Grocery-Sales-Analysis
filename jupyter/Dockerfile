# Dockerfile for Jupyter Notebook
FROM jupyter/base-notebook:latest

RUN mkdir -p /home/jovyan/work && chown -R jovyan:jovyan /home/jovyan
WORKDIR /home/jovyan/work

# Install additional dependencies
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
