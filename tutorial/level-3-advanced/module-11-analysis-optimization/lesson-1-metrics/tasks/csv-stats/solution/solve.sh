#!/bin/bash
cat >/home/user/csv_stats.py <<'PYEOF'
import csv

with open("/home/user/data.csv") as f:
    reader = csv.DictReader(f)
    scores = [int(row["score"]) for row in reader]

print(f"count: {len(scores)}")
print(f"mean: {sum(scores) / len(scores):.1f}")
print(f"max: {max(scores)}")
print(f"min: {min(scores)}")
PYEOF
