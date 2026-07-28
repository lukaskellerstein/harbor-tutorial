"""Reward dimension: "correctness".

The directory name IS the reward name. Everything registered here contributes
to a reward called "correctness" and to nothing else.
"""

from pathlib import Path

import rewardkit as rk
from rewardkit import criteria, criterion

# Shared criteria from ../criteria.py, reached through the `criteria` module.
# Both return floats, so a partially-correct function earns partial credit
# rather than a flat 0.
criteria.word_count_correct(weight=3.0)
criteria.unique_words_correct(weight=3.0)


# A zero-parameter custom criterion auto-registers: defining it here is enough,
# there is no separate call. Contrast with the parameterized one in
# ../structure/files.py, which MUST be called explicitly.
@criterion
def top_word_correct(workspace: Path) -> bool:
    """top_word() picks the right word, and does not crash on empty input."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "textstats", workspace / "textstats.py"
    )
    if spec is None or spec.loader is None:
        return False
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        module.top_word("")  # must not raise
        return module.top_word("the the fox") == "the"
    except Exception:
        return False


# The pipeline's actual output, checked against the known sample.
rk.json_key_equals("results.json", "words", 19, weight=2.0)
rk.json_key_equals("results.json", "unique", 13, weight=2.0)
rk.json_key_equals("results.json", "top_word", "the", weight=2.0)
