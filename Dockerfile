# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Update the package list and install libpq-dev
# Install necessary packages
RUN apt-get update && \
    apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    libffi-dev \
    ffmpeg \
    mpv \
    postgresql-client

# Install any needed packages specified in requirements.txt
# Copying only the requirements.txt file first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy the rest of the current directory contents into the container at /app
COPY . /app

# Run app.py when the container launches
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
