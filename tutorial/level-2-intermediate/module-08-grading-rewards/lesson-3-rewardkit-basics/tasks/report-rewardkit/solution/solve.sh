#!/bin/bash

cat > /app/report.md <<'EOF'
# Quarterly Container Report

## Summary
Container build times dropped by 18% after switching to a slim base image.

## Findings
Layer caching accounts for most of the gain. The remaining time is dominated by
dependency resolution, which is not currently cached between builds.

## Conclusion
Cache the dependency resolution step next. That is the single largest remaining
cost in the build pipeline.
EOF
