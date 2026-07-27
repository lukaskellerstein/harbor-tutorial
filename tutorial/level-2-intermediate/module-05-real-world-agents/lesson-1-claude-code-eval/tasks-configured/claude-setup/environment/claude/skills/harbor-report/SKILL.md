---
name: harbor-report
description: The required format for build reports in this project. Use whenever you are asked to write a build report, or whenever you are about to write /app/report.md.
---

# Build report format

Write `/app/report.md` containing exactly these three lines, in this order:

```
# Build Report
Build-Code: <the code returned by the harbor-demo MCP server's get_build_code tool>
Verified-By: fact-checker
```

Then append the project-wide trailer line required by `CLAUDE.md`.

Do not add any other lines, headings, or commentary to the file.
