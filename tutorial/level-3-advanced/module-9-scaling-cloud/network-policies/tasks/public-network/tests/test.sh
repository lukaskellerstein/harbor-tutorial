#!/bin/bash
if [ -f /home/user/online-result.txt ] && grep -q "solved-online" /home/user/online-result.txt; then
    echo "1.0" > /logs/verifier/reward.txt
else
    echo "0.0" > /logs/verifier/reward.txt
fi
