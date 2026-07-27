#!/bin/bash
cat > /app/check_deps.py << 'PYEOF'
import requests

response = requests.get("https://httpbin.org/get")
with open("/app/status.txt", "w") as f:
    f.write(str(response.status_code))
PYEOF

python /app/check_deps.py
