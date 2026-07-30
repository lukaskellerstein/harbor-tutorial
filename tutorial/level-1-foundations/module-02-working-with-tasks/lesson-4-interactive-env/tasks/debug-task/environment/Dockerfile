FROM python:3.12-slim

# Install additional debugging tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    vim \
    git \
    procps \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Install Python libraries the task might need
RUN pip install --no-cache-dir requests==2.32.3

WORKDIR /app
