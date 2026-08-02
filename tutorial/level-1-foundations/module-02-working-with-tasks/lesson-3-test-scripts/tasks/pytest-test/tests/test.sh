#!/bin/bash

# APPROACH 3: Pytest-based test with CTRF reporting
#
# This approach uses pytest for structured testing and produces
# a CTRF (Common Test Report Format) JSON file alongside the reward.
# This is Harbor's default scaffolding style (harbor task init).

mkdir -p /logs/verifier

# Install uv, then use it to run pytest with the CTRF plugin
curl -LsSf https://astral.sh/uv/install.sh | sh
# shellcheck source=/dev/null  # written by the installer above; absent at lint time
source "$HOME/.local/bin/env"

# Branch on the command directly rather than on $? — pytest's exit status is the
# reward, and a line between the two would silently overwrite it.
if uvx \
  --with pytest==8.4.1 \
  --with pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_state.py -rA; then
  echo 1 >/logs/verifier/reward.txt
else
  echo 0 >/logs/verifier/reward.txt
fi
