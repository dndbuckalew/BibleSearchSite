FROM python:3.11-slim

WORKDIR /app

COPY build_version.txt .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 👇 COPY ENTIRE BACKEND FIRST
COPY . .

# 👇 THEN install from copied file
RUN pip install --no-cache-dir -r backend/requirements.txt

EXPOSE 8080

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
