FROM python:3.13-slim

RUN apt-get update -y \
    && apt-get -y install libraqm-dev

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/usr/local

WORKDIR /app

# Preinstall dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY service_account.json /root/.config/gspread/service_account.json
COPY . .

RUN uv sync --frozen --no-dev
