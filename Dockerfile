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

# The default Fly image requires the pinned release catalog.
FROM runtime AS scripture
ENV BTA_SCRIPTURE_SQLITE_PATH=/app/data/scripture.sqlite
ENV BTA_SCRIPTURE_SQLITE_SHA256=edd8495fd4a9db18e28f95665621e964d1fb49992073292aa744b0e148008c0f
COPY --chmod=0444 data/scripture.sqlite /app/data/scripture.sqlite
COPY tools/scripture/release-catalog.json tools/scripture/verify_release_bundle.py tools/scripture/
RUN --network=none OPENAI_API_KEY=offline-verification python -m tools.scripture.verify_release_bundle

FROM scripture AS app
