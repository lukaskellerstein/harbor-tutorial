"""Run the text-analysis pipeline over sample.txt."""

import json
from pathlib import Path

import textstats


def main() -> None:
    text = Path("sample.txt").read_text()
    results = {
        "words": textstats.word_count(text),
        "unique": textstats.unique_words(text),
        "top_word": textstats.top_word(text),
    }
    Path("results.json").write_text(json.dumps(results, indent=2))
    print("OK")


if __name__ == "__main__":
    main()
