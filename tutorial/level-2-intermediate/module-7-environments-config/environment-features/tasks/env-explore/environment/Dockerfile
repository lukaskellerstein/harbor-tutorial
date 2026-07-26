FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        curl \
        jq \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Pre-populate data files for the agent to discover
RUN mkdir -p /app/data /app/results

RUN echo '{"name": "harbor-demo", "version": "1.0", "debug": false}' > /app/data/config.json
RUN echo "This is a sample log entry." > /app/data/sample.log
RUN echo "key=value" > /app/data/settings.env
