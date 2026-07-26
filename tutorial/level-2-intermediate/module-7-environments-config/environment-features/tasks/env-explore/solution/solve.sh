#!/bin/bash
mkdir -p /app/results
ls -la /app/data/ > /app/results/listing.txt
cat /app/data/config.json > /app/results/config_copy.txt
echo "=== System Info ===" > /app/results/environment_info.txt
uname -a >> /app/results/environment_info.txt
whoami >> /app/results/environment_info.txt
