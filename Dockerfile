FROM python:3.12-slim

RUN apt-get update -y  \
    && apt-get -y install libraqm-dev \
    && python -m pip install poetry

ENV PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Preinstall dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --no-root

COPY service_account.json /root/.config/gspread/service_account.json
COPY . .

RUN poetry install --no-interaction --no-ansi --only-root
