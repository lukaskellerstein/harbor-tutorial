#!/bin/bash
mkdir -p /app/project
echo '{"name": "demo", "version": "1.0", "entries": 5}' >/app/project/config.json
cat <<'EOF' >/app/project/generate.py
import json

with open("/app/project/config.json") as f:
    config = json.load(f)

n = config["entries"]
with open("/app/project/output.txt", "w") as f:
    for i in range(1, n + 1):
        f.write(f"Entry {i}\n")
EOF
python3 /app/project/generate.py
