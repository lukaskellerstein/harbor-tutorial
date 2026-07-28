"""Reward dimension: "process" -- HOW did the agent get there?

The outcome dimension cannot tell "wrote a script that sorts" from "read the
eight numbers and typed them out in order". The trajectory can.

PATH GOTCHA
-----------
All three trajectory criteria default to path="/logs/trajectory.json".
Harbor agents write ATIF to /logs/agent/trajectory.json -- the agent's log
directory, not the root of /logs. The default is therefore wrong for every
Harbor task, and it fails SILENTLY: load_trajectory() returns None for a
missing file, and the criterion scores 0 with no error. A whole process
dimension reading zero looks like a badly behaved agent, not a typo.

Always pass `path=` explicitly.
"""

import rewardkit as rk

TRAJECTORY = "/logs/agent/trajectory.json"

# The instruction said to write and run a script. These check that it did.
rk.trajectory_tool_used("Write", path=TRAJECTORY, weight=2.0)
rk.trajectory_tool_used("Bash", path=TRAJECTORY, weight=2.0)

# It should have looked at the input rather than guessing.
rk.trajectory_tool_used("Read", min_count=1, path=TRAJECTORY)

# Efficiency, with partial credit rather than a cliff: 1.0 at or under
# max_turns, decaying linearly to 0.0 at 2 * max_turns.
rk.trajectory_turn_count(6, path=TRAJECTORY, weight=1.0)
