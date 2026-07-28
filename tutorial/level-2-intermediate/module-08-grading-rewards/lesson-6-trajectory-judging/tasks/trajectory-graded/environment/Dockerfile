FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY numbers.txt /app/numbers.txt

# A RECORDED agent trajectory, so this lesson runs with the free `oracle` agent.
# In a real run the agent writes /logs/agent/trajectory.json itself; solve.sh
# stages this copy there instead. Run with `-a claude-code` and the file is real.
COPY recorded-trajectory.json /app/recorded-trajectory.json
