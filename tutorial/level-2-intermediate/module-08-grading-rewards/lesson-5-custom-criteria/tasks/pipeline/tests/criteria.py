"""Custom criteria SHARED across the reward dimensions.

This file sits at the root of tests/, next to the subdirectories. That placement
comes with a rule (rewardkit/runner.py:discover): when subdirectories exist,
every criterion defined in a root-level .py file MUST be marked
`@criterion(shared=True)`. Otherwise discovery raises

    ValueError: Root-level criteria 'x' in /tests would be ignored in nested
    layout (subdirectories exist). Either move them into a subdirectory or mark
    them @criterion(shared=True).

The reasoning: root files are imported first purely so subdirectories can call
what they define. A non-shared criterion registered there would belong to no
dimension and silently never run -- so RewardKit refuses instead.
"""

import importlib.util
from pathlib import Path

from rewardkit import criterion

# Known-good input/output pairs. Testing the agent's FUNCTION beats testing its
# output file: results.json can be hardcoded, word_count() cannot.
WORD_COUNT_CASES = [
    ("a b c", 3),
    ("", 0),
    ("one", 1),
    ("  padded   words  ", 2),
]

UNIQUE_WORD_CASES = [
    ("a b c", 3),
    ("a a a", 1),
    ("", 0),
    ("the the fox", 2),
]


def _load_module(workspace: Path, name: str):
    """Import a module out of the agent's workspace without touching sys.path."""
    spec = importlib.util.spec_from_file_location(name, workspace / f"{name}.py")
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot find {name}.py in workspace")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _score_cases(workspace: Path, func_name: str, cases: list) -> float:
    """Fraction of cases the agent's function gets right. 0.0 if it will not load."""
    try:
        textstats = _load_module(workspace, "textstats")
        func = getattr(textstats, func_name)
    except Exception:
        return 0.0

    passed = 0
    for text, expected in cases:
        try:
            if func(text) == expected:
                passed += 1
        except Exception:
            # A crash on one input is just that input failing, not a zero.
            pass
    return passed / len(cases)


@criterion(shared=True)
def word_count_correct(workspace: Path) -> float:
    """Fraction of word_count() cases that pass."""
    return _score_cases(workspace, "word_count", WORD_COUNT_CASES)


@criterion(shared=True)
def unique_words_correct(workspace: Path) -> float:
    """Fraction of unique_words() cases that pass."""
    return _score_cases(workspace, "unique_words", UNIQUE_WORD_CASES)
