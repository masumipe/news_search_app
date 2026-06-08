FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r newsapp && useradd -r -g newsapp -d /app -s /bin/bash newsapp

COPY pyproject.toml .
RUN pip install --no-cache-dir . && pip install --no-cache-dir gunicorn

COPY --chown=newsapp:newsapp src/ ./src/
COPY --chown=newsapp:newsapp migrations/ ./migrations/

USER newsapp

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "src.news_app.app:create_app()"]
