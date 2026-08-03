#!/bin/bash
cat <<'EOF' >/app/word_counter.py
def count_words(filepath: str) -> tuple[int, int]:
    with open(filepath) as f:
        text = f.read()
    words = text.split()
    total = len(words)
    unique = len(set(w.lower() for w in words))
    return total, unique

total, unique = count_words("/app/sample.txt")
with open("/app/report.txt", "w") as f:
    f.write(f"Total words: {total}\n")
    f.write(f"Unique words: {unique}\n")
EOF
python3 /app/word_counter.py
