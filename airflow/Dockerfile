# https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile
# Dependency Builder using UV
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# use Airflow image as final image
FROM apache/airflow:2.10.5-python3.12

WORKDIR /opt/airflow

USER root
COPY --from=builder --chown=airflow:root /app /opt/airflow

ENV PATH="/opt/airflow/.venv/bin:$PATH"

USER airflow
