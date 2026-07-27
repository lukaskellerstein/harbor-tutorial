"""A minimal stdio MCP server for the Harbor tutorial.

It exposes a single tool that returns a build code. Nothing else in the
container can produce that value, so finding it in /app/report.md proves the
MCP server was actually connected and called -- which is what makes this task
a real test of the project-scoped .mcp.json rather than of the model's guessing.

Runs entirely locally over stdio, so the task needs no network at run time.
"""

from mcp.server.fastmcp import FastMCP

BUILD_CODE = "HRB-7391"

mcp = FastMCP("harbor-demo")


@mcp.tool()
def get_build_code() -> str:
    """Return the current build code for this project."""
    return BUILD_CODE


if __name__ == "__main__":
    mcp.run()
