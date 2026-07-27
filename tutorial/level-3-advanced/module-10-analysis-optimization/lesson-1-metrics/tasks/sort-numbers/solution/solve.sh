#!/bin/bash
cat > /home/user/sort_numbers.py << 'PYEOF'
with open("/home/user/numbers.txt") as f:
    numbers = [int(line.strip()) for line in f if line.strip()]
numbers.sort()
with open("/home/user/sorted.txt", "w") as f:
    for n in numbers:
        f.write(f"{n}\n")
PYEOF
