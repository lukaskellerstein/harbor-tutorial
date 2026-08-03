#!/bin/bash
cat >/workspace/fibonacci.py <<'PYEOF'
def fibonacci(n: int) -> list[int]:
    if n <= 0:
        return []
    if n == 1:
        return [0]
    fibs = [0, 1]
    for _ in range(2, n):
        fibs.append(fibs[-1] + fibs[-2])
    return fibs

for num in fibonacci(10):
    print(num)
PYEOF
