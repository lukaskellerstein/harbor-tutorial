#!/bin/bash

# Reference solution: create the word-counting script.
# The oracle agent runs this file to validate the task setup.

cat > /app/count_words.py << 'PYTHON'
def main():
    with open("/app/input.txt", "r") as f:
        text = f.read()
    word_count = len(text.split())
    print(word_count)

if __name__ == "__main__":
    main()
PYTHON

echo "Solution created successfully."
