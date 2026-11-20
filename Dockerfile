# syntax=docker/dockerfile:1
FROM python:3.11-slim AS runtime

WORKDIR /app

COPY build_version.txt .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/ backend/
COPY tools/scripture/import_kjv.py tools/scripture/kjv-manifest.json tools/scripture/

RUN pip install --no-cache-dir -r backend/requirements.txt

EXPOSE 8080

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]

# The deployment workflow supplies the verified SQLite file in the build context.
FROM runtime AS scripture
ARG SCRIPTURE_BUNDLE_SHA256
ENV BTA_SCRIPTURE_SQLITE_PATH=/app/data/scripture.sqlite
ENV BTA_SCRIPTURE_SQLITE_SHA256=${SCRIPTURE_BUNDLE_SHA256}
RUN install -d -m 0755 /app/data
COPY --chmod=0444 scripture.sqlite /app/data/scripture.sqlite
RUN python -c "from backend.services.scripture_retrieval import sqlite_connection; conn=sqlite_connection(); assert conn.execute('PRAGMA quick_check').fetchone() == ('ok',); assert conn.execute('SELECT COUNT(DISTINCT edition) FROM snapshot').fetchone() == (15,); conn.close()"

# Existing builds continue to select this target unless scripture is requested.
FROM runtime AS app
