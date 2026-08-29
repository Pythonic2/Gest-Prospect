#!/usr/bin/env python3
"""Gera os arquivos Docker padronizados deste projeto Django."""

import argparse
from pathlib import Path


DOCKERFILE = """FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    UV_COMPILE_BYTECODE=1 \\
    UV_LINK_MODE=copy \\
    PATH=/app/.venv/bin:$PATH

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /uvx /bin/
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY manage.py ./

RUN uv sync --frozen --no-dev \\
    && uv run python manage.py collectstatic --noinput \\
    && mkdir -p /app/data \\
    && useradd --create-home --uid 10001 django \\
    && chown -R django:django /app

USER django

ENV APP_PORT=__PORT__ \\
    DATABASE_PATH=/app/data/db.sqlite3

EXPOSE __PORT__

CMD ["/bin/sh", "-c", "python manage.py migrate && exec gunicorn __MODULE__.wsgi:application --bind 0.0.0.0:${APP_PORT:-__PORT__} --workers ${GUNICORN_WORKERS:-2} --timeout ${GUNICORN_TIMEOUT:-60}"]
"""

COMPOSE = """name: __PROJECT__

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: __PROJECT__-app
    environment:
      GOOGLE_MAPS_API_KEY: "${GOOGLE_MAPS_API_KEY:-}"
      DJANGO_SECRET_KEY: "${DJANGO_SECRET_KEY:-dev-only-change-me}"
      APP_PORT: "${APP_PORT:-__PORT__}"
      APP_URL: "${APP_URL:-http://localhost:__PORT__}"
      DJANGO_DEBUG: "${DJANGO_DEBUG:-false}"
      DJANGO_ALLOWED_HOSTS: "${DJANGO_ALLOWED_HOSTS:-localhost,127.0.0.1}"
      DJANGO_CSRF_TRUSTED_ORIGINS: "${DJANGO_CSRF_TRUSTED_ORIGINS:-http://localhost:__PORT__}"
      DJANGO_SECURE_SSL_REDIRECT: "${DJANGO_SECURE_SSL_REDIRECT:-false}"
      GUNICORN_WORKERS: "${GUNICORN_WORKERS:-2}"
      GUNICORN_TIMEOUT: "${GUNICORN_TIMEOUT:-60}"
      DATABASE_PATH: /app/data/db.sqlite3
    ports:
      - "${APP_PORT:-__PORT__}:${APP_PORT:-__PORT__}"
    volumes:
      - django_data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('APP_PORT', '__PORT__') + '/', timeout=3)"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 20s

volumes:
  django_data:
"""

DOCKERIGNORE = """.git
.gitignore
.venv
__pycache__
*.py[cod]
.env
db.sqlite3
staticfiles
.pytest_cache
.ruff_cache
*.log
"""


def render(template: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        template = template.replace(f"__{key}__", value)
    return template


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8003)
    parser.add_argument("--project", default="gest-prospect")
    parser.add_argument("--module", default="gest_prospect")
    parser.add_argument("--output", type=Path, default=Path.cwd())
    args = parser.parse_args()

    if not 1 <= args.port <= 65535:
        parser.error("a porta deve estar entre 1 e 65535")

    args.output.mkdir(parents=True, exist_ok=True)
    values = {"PORT": str(args.port), "PROJECT": args.project, "MODULE": args.module}
    files = {
        "Dockerfile": render(DOCKERFILE, values),
        "docker-compose.yml": render(COMPOSE, values),
        ".dockerignore": DOCKERIGNORE,
    }
    for filename, content in files.items():
        path = args.output / filename
        path.write_text(content, encoding="utf-8")
        print(f"Gerado: {path}")


if __name__ == "__main__":
    main()
