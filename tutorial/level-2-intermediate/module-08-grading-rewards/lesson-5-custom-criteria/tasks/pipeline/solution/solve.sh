#!/bin/bash

cat > /app/textstats.py <<'EOF'
"""Word statistics helpers."""

from collections import Counter


def word_count(text: str) -> int:
    """Number of whitespace-separated words in text."""
    return len(text.split())


def unique_words(text: str) -> int:
    """Number of distinct whitespace-separated words in text."""
    return len(set(text.split()))


def top_word(text: str) -> str:
    """The most frequently occurring word, or "" for empty input."""
    words = text.split()
    if not words:
        return ""
    return Counter(words).most_common(1)[0][0]
EOF

cat > /app/analyze.py <<'EOF'
"""Run the text-analysis pipeline over sample.txt."""

import json
from pathlib import Path

import textstats


def main() -> None:
    text = Path("/app/sample.txt").read_text()
    results = {
        "words": textstats.word_count(text),
        "unique": textstats.unique_words(text),
        "top_word": textstats.top_word(text),
    }
    Path("/app/results.json").write_text(json.dumps(results, indent=2))
    print("OK")


if __name__ == "__main__":
    main()
EOF

cd /app && python analyze.py
