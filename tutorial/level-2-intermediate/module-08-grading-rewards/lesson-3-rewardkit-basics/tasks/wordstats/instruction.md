Write a Python script at `/app/wordstats.py` that analyses `/app/sample.txt`.

The script must:

1. Define a function `word_count(text)` that returns the number of whitespace-separated words in `text`.
2. When run as `python wordstats.py` from `/app`, write `/app/results.json` containing exactly these keys:
   - `words` — total number of words in the file
   - `lines` — number of non-empty lines
   - `top_word` — the most frequently occurring word
3. Print `OK` to stdout when it finishes successfully.
4. Run the script, so that `/app/results.json` already exists when you are done.
