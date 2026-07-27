#!/bin/bash
if [ -f /home/user/offline-result.txt ] && grep -q "solved-offline" /home/user/offline-result.txt; then
    echo "1.0" > /logs/verifier/reward.txt
else
    echo "0.0" > /logs/verifier/reward.txt
fi
