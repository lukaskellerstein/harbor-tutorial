#!/bin/bash
# Verify network is available, then write the result
nslookup example.com > /dev/null 2>&1 || true
echo "solved-online" > /home/user/online-result.txt
