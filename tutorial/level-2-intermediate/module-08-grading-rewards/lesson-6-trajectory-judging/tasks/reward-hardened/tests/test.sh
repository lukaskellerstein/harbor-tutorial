#!/bin/bash
# The same honest verifier, plus one line of hygiene.
#
# DEFENCE 1: clear the reward directory before writing to it.
#
# The verifier runs after the agent, on a filesystem the agent could write to.
# Anything already in /logs/verifier is untrusted input. Deleting stale reward
# files first means the verifier's verdict is the only verdict, whichever file
# format it happens to use.
#
# This costs one line and works in every environment mode. Do it always.

mkdir -p /logs/verifier
rm -f /logs/verifier/reward.json /logs/verifier/reward.txt

EXPECTED="1
3
7
15
19
23
42
88"

if [ -f /app/sorted.txt ] && [ "$(cat /app/sorted.txt)" = "$EXPECTED" ]; then
    echo "sorted.txt is correct"
    echo "1" > /logs/verifier/reward.txt
else
    echo "sorted.txt is missing or wrong -- this trial FAILED"
    echo "0" > /logs/verifier/reward.txt
fi
