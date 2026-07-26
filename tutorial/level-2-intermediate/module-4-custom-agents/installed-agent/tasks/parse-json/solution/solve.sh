#!/bin/bash
cat /home/user/data.json | python3 -c "import sys,json; print(json.load(sys.stdin)['result'])" > /home/user/output.txt
