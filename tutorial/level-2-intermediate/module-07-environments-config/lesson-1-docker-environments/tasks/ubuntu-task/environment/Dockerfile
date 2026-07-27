# Simple Ubuntu-based Dockerfile
# Demonstrates: general-purpose base image with apt-get installs
FROM ubuntu:24.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install basic utilities the agent might need
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        lsb-release \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
