#!/bin/bash

cat >/app/wordstats.py <<'EOF'
"""Word statistics for sample.txt."""

import json
from collections import Counter
from pathlib import Path


def word_count(text: str) -> int:
    """Number of whitespace-separated words in text."""
    return len(text.split())


def main() -> None:
    text = Path("/app/sample.txt").read_text()
    words = text.split()
    lines = [line for line in text.splitlines() if line.strip()]

    results = {
        "words": word_count(text),
        "lines": len(lines),
        "top_word": Counter(words).most_common(1)[0][0],
    }
    Path("/app/results.json").write_text(json.dumps(results, indent=2))
    print("OK")


if __name__ == "__main__":
    main()
EOF

# Produce results.json now. The verifier's criteria run CONCURRENTLY, so a
# criterion that reads results.json cannot rely on another criterion having
# created it first.
cd /app && python wordstats.py
