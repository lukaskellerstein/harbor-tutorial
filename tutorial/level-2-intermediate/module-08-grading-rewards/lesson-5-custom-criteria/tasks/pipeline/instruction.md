Build a small text-analysis pipeline in `/app`.

1. `/app/textstats.py` must define three functions:
   - `word_count(text)` — number of whitespace-separated words
   - `unique_words(text)` — number of distinct words
   - `top_word(text)` — the most frequently occurring word

2. `/app/analyze.py` must import `textstats`, read `/app/sample.txt`, and write
   `/app/results.json` with exactly these keys:
   - `words`, `unique`, `top_word`

3. Run `analyze.py` so that `/app/results.json` already exists when you are done.

Write readable code: docstrings, sensible names, and handle empty input without crashing.
