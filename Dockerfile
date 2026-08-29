FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH=/app/.venv/bin:$PATH

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /uvx /bin/
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY manage.py ./

RUN uv sync --frozen --no-dev \
    && DB_NAME=build DB_USER=build DB_PASSWORD=build DB_HOST=localhost uv run python manage.py collectstatic --noinput \
    && useradd --create-home --uid 10001 django \
    && chown -R django:django /app

USER django

ENV APP_PORT=8003

EXPOSE 8003

CMD ["/bin/sh", "-c", "python manage.py migrate && exec gunicorn gest_prospect.wsgi:application --bind 0.0.0.0:${APP_PORT:-8003} --workers ${GUNICORN_WORKERS:-2} --timeout ${GUNICORN_TIMEOUT:-60}"]
