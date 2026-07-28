#!/bin/bash

cat > /app/report.md <<'EOF'
# Quarterly Container Report

## Summary
Container build times dropped by 18% after switching to a slim base image, and
the change required no application code edits at all.

## Findings
Layer caching accounts for most of the gain. The remaining time is dominated by
dependency resolution, which is not currently cached between builds and so runs
from scratch on every single pipeline invocation.

## Conclusion
Cache the dependency resolution step next. That is the single largest remaining
cost in the build pipeline, and it should be straightforward to address.
EOF
