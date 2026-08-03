#!/bin/bash
cat >/home/user/transform.py <<'PYEOF'
import json

with open("/home/user/input.json") as f:
    data = json.load(f)

filtered = [p for p in data if p["age"] >= 18]
filtered.sort(key=lambda p: p["age"])

with open("/home/user/output.json", "w") as f:
    json.dump(filtered, f, separators=(",", ":"))
PYEOF
