#!/bin/bash
cat >/home/user/reverse.py <<'PYEOF'
import sys
text = sys.stdin.read().strip()
print(text[::-1], end="")
PYEOF
