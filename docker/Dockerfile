# Dockerfile for Automated Job Market Analytics Platform
# Build Context: Root directory of the repository (e.g. docker build -f docker/Dockerfile -t job-analytics .)

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DBT_PROFILES_DIR=/app/dbt_project

WORKDIR /app

# Install PostgreSQL client headers and build dependencies for compiling psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . /app/

# Create folders for data snapshots (raw/processed)
RUN mkdir -p /app/data/raw /app/data/processed

# Default execution command is to run the scraper python package
CMD ["python", "scraper/main.py"]
