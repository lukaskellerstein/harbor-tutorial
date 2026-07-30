"""RewardKit criteria for the wordstats task.

This file is not a test suite that gets imported and called -- RewardKit
executes it top to bottom and each `rk.<criterion>(...)` call REGISTERS a check.
The module-level calls below are the whole verifier.

Because tests/ has no subdirectories, this is a "flat" layout: every criterion
here contributes to a single reward named "reward".

IMPORTANT: criteria run CONCURRENTLY (rewardkit/reward.py runs them in an
asyncio.TaskGroup, up to --max-concurrent-programmatic at a time). Registration
order is not execution order. So a criterion must never depend on a side effect
that another criterion produces -- the json_key_equals calls below read a
results.json the AGENT was asked to create, not one command_succeeds happens to
leave behind.
"""

# The imports below are provided by the task container image, not by this
# lesson's virtualenv, so they do not resolve when you open this file locally.
# pyright: reportMissingImports=false, reportMissingModuleSource=false

import rewardkit as rk

# --- structure: did the agent produce the artifact we asked for? ------------
rk.file_exists("wordstats.py")
rk.file_contains("wordstats.py", "def word_count")

# --- behaviour: does it actually run, and announce success? -----------------
# Paths are relative to the workspace (/app by default), so no absolute paths.
rk.command_succeeds("python wordstats.py", weight=2.0)
rk.command_output_matches("python wordstats.py", "OK")

# --- correctness: are the numbers right? ------------------------------------
# results.json is the agent's artifact -- the instruction told them to run the
# script. Do NOT assume command_succeeds above created it; see the module
# docstring on concurrency.
#
# Weighted heaviest: a script that runs but computes garbage is worth less than
# one that computes correctly. Weights are relative, not percentages.
rk.json_key_equals("results.json", "words", 19, weight=3.0)
rk.json_key_equals("results.json", "lines", 3, weight=3.0)
rk.json_key_equals("results.json", "top_word", "the", weight=3.0)
