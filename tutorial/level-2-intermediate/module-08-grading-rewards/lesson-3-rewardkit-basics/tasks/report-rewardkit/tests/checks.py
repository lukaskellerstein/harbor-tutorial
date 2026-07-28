"""Lesson 1's reward-txt verifier, rewritten.

The bash original was ~20 lines: a loop, a counter, an awk invocation to compute
the fraction, and a redirect into reward.txt. This is the same three checks and
the same 0.00 / 0.33 / 0.67 / 1.00 scale -- RewardKit does the averaging.

`file_contains` returns False (with a warning) when the file is missing, so
there is no separate existence check to write.
"""

import rewardkit as rk

rk.file_contains("report.md", "## Summary")
rk.file_contains("report.md", "## Findings")
rk.file_contains("report.md", "## Conclusion")
