#!/bin/bash

cat >/app/sort_numbers.py <<'EOF'
"""Sort the integers in numbers.txt into sorted.txt."""

from pathlib import Path


def main() -> None:
    numbers = [int(line) for line in Path("/app/numbers.txt").read_text().split()]
    numbers.sort()
    Path("/app/sorted.txt").write_text("\n".join(str(n) for n in numbers) + "\n")


if __name__ == "__main__":
    main()
EOF

cd /app && python sort_numbers.py

# Stage the recorded trajectory where a real agent would have written its own.
# The `oracle` agent does not produce one -- it just runs this script -- so the
# lesson ships a recording to keep the trajectory criteria demonstrable for
# free. Run this task with `-a claude-code` and this line becomes unnecessary.
mkdir -p /logs/agent
cp /app/recorded-trajectory.json /logs/agent/trajectory.json
