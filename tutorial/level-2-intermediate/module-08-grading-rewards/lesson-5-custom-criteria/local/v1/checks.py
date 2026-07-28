"""Candidate verifier v1 -- grades the OUTPUT.

Checks that the expected files exist and that results.json holds the right
numbers for the sample input. Entirely reasonable-looking.
"""

import rewardkit as rk

rk.file_exists("textstats.py")
rk.file_exists("analyze.py")
rk.json_key_equals("results.json", "words", 19)
rk.json_key_equals("results.json", "unique", 13)
rk.json_key_equals("results.json", "top_word", "the")
