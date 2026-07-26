#!/bin/bash
if [ -f /home/user/result.txt ] && grep -q "task-1-complete" /home/user/result.txt; then
    echo "1.0" > /logs/verifier/reward.txt
else
    echo "0.0" > /logs/verifier/reward.txt
fi
