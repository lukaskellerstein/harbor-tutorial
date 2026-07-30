"""Reward dimension: "outcome" -- did the agent produce the right artifact?

The ordinary kind of grading, here only so there is something to contrast the
process dimension against.
"""

# The imports below are provided by the task container image, not by this
# lesson's virtualenv, so they do not resolve when you open this file locally.
# pyright: reportMissingImports=false, reportMissingModuleSource=false

import rewardkit as rk

rk.file_exists("sort_numbers.py")
rk.file_matches("sorted.txt", "1\n3\n7\n15\n19\n23\n42\n88")
