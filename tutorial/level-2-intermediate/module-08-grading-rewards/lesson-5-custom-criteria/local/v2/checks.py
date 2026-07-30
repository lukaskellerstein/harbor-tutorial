"""Candidate verifier v2 -- grades the FUNCTION.

Same files, same task, but it calls word_count() with inputs the sample file
never contains. That is the difference between "produced the right answer once"
and "implemented the thing we asked for".
"""

import contextlib
import importlib.util
from pathlib import Path

import rewardkit as rk
from rewardkit import criterion

CASES = [
    ("a b c", 3),
    ("", 0),  # "".split(" ") is [""], so a naive split scores 1 here
    ("one", 1),
    ("  padded   words  ", 2),  # repeated spaces break a literal-space split
]


@criterion(description="word_count() is correct on {n} held-out inputs")
def word_count_correct(workspace: Path, n: int) -> float:
    """Fraction of held-out cases the agent's word_count() gets right."""
    spec = importlib.util.spec_from_file_location(
        "textstats", workspace / "textstats.py"
    )
    if spec is None or spec.loader is None:
        return 0.0
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    # The agent wrote this module, so importing it can raise anything at all.
    except Exception:  # noqa: BLE001
        return 0.0

    passed = 0
    for text, expected in CASES[:n]:
        # A crash on one input is just that input failing, not a zero.
        with contextlib.suppress(Exception):
            if module.word_count(text) == expected:
                passed += 1
    return passed / n


rk.file_exists("textstats.py")
rk.file_exists("analyze.py")
rk.json_key_equals("results.json", "words", 19)
rk.json_key_equals("results.json", "unique", 13)
rk.json_key_equals("results.json", "top_word", "the")
rk.word_count_correct(4, weight=5.0)
