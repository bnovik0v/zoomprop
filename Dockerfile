# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Update the package list and install necessary packages
RUN apt-get update && \
    apt-get install -y \
    gcc \
    python3-dev \
    libffi-dev \
    sqlite3 
    
# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the current directory contents into the container at /app
COPY . /app

# Run app.py when the container launches
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
