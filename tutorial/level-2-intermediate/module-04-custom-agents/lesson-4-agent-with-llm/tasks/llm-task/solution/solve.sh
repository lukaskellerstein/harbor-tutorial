#!/bin/bash
cat >/home/user/primes.py <<'PYEOF'
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def largest_prime_below(limit: int) -> int:
    for n in range(limit - 1, 1, -1):
        if is_prime(n):
            return n
    return 2

print(largest_prime_below(1000))
PYEOF
