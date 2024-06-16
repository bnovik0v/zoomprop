# Use an official Python runtime as a parent image
FROM python:3.10-slim AS base

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libffi-dev \
    sqlite3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies in a separate step
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the necessary files
COPY ./app /app/app
COPY ./gunicorn.conf.py /app/gunicorn.conf.py

# Copy data and other necessary files
COPY .env /app/.env

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
