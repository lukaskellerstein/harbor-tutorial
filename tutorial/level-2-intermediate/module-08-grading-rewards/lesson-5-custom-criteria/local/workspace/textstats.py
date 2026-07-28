"""Word statistics helpers.

A SUBTLY BROKEN implementation, used to compare two candidate verifiers.

word_count splits on a literal single space instead of on whitespace. On the
sample file -- which has no double spaces and no blank lines -- it produces
exactly the right answer, so results.json looks perfect. It is still wrong:
`"".split(" ")` is `[""]`, so an empty string counts as one word.
"""

from collections import Counter


def word_count(text: str) -> int:
    """Number of words in text."""
    return len(text.split(" "))


def unique_words(text: str) -> int:
    """Number of distinct words in text."""
    return len(set(text.split()))


def top_word(text: str) -> str:
    """The most frequently occurring word."""
    words = text.split()
    if not words:
        return ""
    return Counter(words).most_common(1)[0][0]
