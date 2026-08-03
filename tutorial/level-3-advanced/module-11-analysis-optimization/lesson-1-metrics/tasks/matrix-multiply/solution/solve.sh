#!/bin/bash
cat >/home/user/matrix_mul.py <<'PYEOF'
def read_matrix(path: str) -> list[list[int]]:
    with open(path) as f:
        return [[int(x) for x in line.split()] for line in f if line.strip()]

def multiply(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    rows_a, cols_a = len(a), len(a[0])
    cols_b = len(b[0])
    result = [[0] * cols_b for _ in range(rows_a)]
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += a[i][k] * b[k][j]
    return result

a = read_matrix("/home/user/matrix_a.txt")
b = read_matrix("/home/user/matrix_b.txt")
c = multiply(a, b)

with open("/home/user/result.txt", "w") as f:
    for row in c:
        f.write(" ".join(str(x) for x in row) + "\n")
PYEOF
