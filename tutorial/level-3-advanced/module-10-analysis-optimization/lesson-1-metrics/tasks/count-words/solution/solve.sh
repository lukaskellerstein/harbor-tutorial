#!/bin/bash
cat > /home/user/count_words.py << 'PYEOF'
with open("/home/user/input.txt") as f:
    text = f.read()
print(len(text.split()))
PYEOF
