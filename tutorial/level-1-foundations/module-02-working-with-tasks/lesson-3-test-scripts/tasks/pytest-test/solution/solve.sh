#!/bin/bash

cat >/app/string_utils.py <<'PYTHON'
def reverse_string(s: str) -> str:
    return s[::-1]

def count_vowels(s: str) -> int:
    return sum(1 for c in s.lower() if c in "aeiou")
PYTHON

echo "string_utils solution created."
