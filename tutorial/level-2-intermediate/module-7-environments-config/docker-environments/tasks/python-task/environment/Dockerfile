# Language-specific Dockerfile
# Demonstrates: using a slim Python base image with pip installs
FROM python:3.12-slim

# Install Python packages the task needs
RUN pip install --no-cache-dir requests==2.32.3

WORKDIR /app

# Pre-populate a sample data file for the task
RUN echo '{"sample": "data", "count": 42}' > /app/sample_data.json
