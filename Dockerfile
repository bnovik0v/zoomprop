FROM python:3.10-slim AS base

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libffi-dev \
    sqlite3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app
COPY ./gunicorn.conf.py /app/gunicorn.conf.py

COPY .env /app/.env

EXPOSE 8000

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
