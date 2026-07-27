Write a build report to /app/report.md.

This project ships its own Claude Code configuration. Use all three parts of it:

1. Call the `get_build_code` tool on the `harbor-demo` MCP server to obtain the
   build code. Do not guess the code — only that tool knows it.
2. Delegate verification of the build code to the `fact-checker` subagent.
3. Follow the project's build-report skill for the exact file format.
