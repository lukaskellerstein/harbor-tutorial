#!/bin/bash

mkdir -p /logs/verifier

# Check the script exists
if [ ! -f /app/fetch_status.py ]; then
    echo "FAIL: /app/fetch_status.py does not exist"
    echo 0 > /logs/verifier/reward.txt
    exit 0
fi

# Run the script
OUTPUT=$(python /app/fetch_status.py 2>&1)
echo "Script output: $OUTPUT"

# Check that the response file was saved
if [ -f /app/response.html ]; then
    FILESIZE=$(wc -c < /app/response.html)
    echo "response.html size: $FILESIZE bytes"
    if [ "$FILESIZE" -gt 0 ]; then
        echo "PASS: Script ran and saved response"
        echo 1 > /logs/verifier/reward.txt
    else
        echo "FAIL: response.html is empty"
        echo 0 > /logs/verifier/reward.txt
    fi
else
    echo "FAIL: /app/response.html not found"
    echo 0 > /logs/verifier/reward.txt
fi
