#!/bin/bash
cat >/home/user/reverse.py <<'PYEOF'
with open("/home/user/input.txt") as f:
    content = f.read().strip()
print(content[::-1])
PYEOF
