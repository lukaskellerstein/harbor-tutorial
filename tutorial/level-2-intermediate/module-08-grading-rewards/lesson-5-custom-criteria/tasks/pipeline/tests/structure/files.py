"""Reward dimension: "structure".

Did the agent build the shape we asked for, regardless of whether the numbers
come out right?
"""

from pathlib import Path

import rewardkit as rk
from rewardkit import criterion

rk.file_exists("textstats.py")
rk.file_exists("analyze.py")
rk.file_exists("results.json")

# analyze.py must actually use the library, not reimplement it inline.
rk.file_contains("analyze.py", "textstats")


# A PARAMETERIZED custom criterion. The description is str.format-ed with the
# bound arguments, so each call gets its own readable name in reward-details.
#
# Unlike the zero-parameter form, defining this does NOT register anything --
# RewardKit cannot guess what `n` should be. You must call it. Forgetting to
# earns a warning:
#
#     UserWarning: Criterion 'defines_n_functions' was defined with @criterion
#     but never called.
@criterion(description="textstats.py defines at least {n} public functions")
def defines_n_functions(workspace: Path, n: int) -> bool:
    source = (workspace / "textstats.py").read_text()
    return sum(1 for line in source.splitlines() if line.startswith("def ")) >= n


# Call it through the module, never as defines_n_functions(3) -- see the README.
rk.defines_n_functions(3, weight=2.0)
