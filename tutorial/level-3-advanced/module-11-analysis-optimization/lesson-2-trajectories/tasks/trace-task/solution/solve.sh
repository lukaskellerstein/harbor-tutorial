#!/bin/bash
cat >/home/user/greeting.py <<'PYEOF'
print("Hello, Harbor!")
PYEOF

cat >/home/user/config.json <<'JSONEOF'
{"name": "harbor", "version": "1.0", "enabled": true}
JSONEOF

echo "Setup complete." >/home/user/summary.txt
