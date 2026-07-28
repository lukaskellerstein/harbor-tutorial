"""Reward dimension: "outcome" -- did the agent produce the right artifact?

The ordinary kind of grading, here only so there is something to contrast the
process dimension against.
"""

import rewardkit as rk

rk.file_exists("sort_numbers.py")
rk.file_matches("sorted.txt", "1\n3\n7\n15\n19\n23\n42\n88")
