"""
Lesson 5: Claude Agent SDK in Harbor

Wrap the Claude Agent SDK as a Harbor BaseAgent. The SDK provides
programmatic access to Claude Code with tool use, permission control,
and agentic loops -- all managed through a Python API.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


LESSON_DIR = Path(__file__).parent


def check_prerequisites() -> bool:
    """Verify Docker, Harbor CLI, and API keys."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
    print("=" * 60)

    ok = True

    if shutil.which("docker"):
        result = subprocess.run(["docker", "info"], capture_output=True, text=True)
        if result.returncode == 0:
            print("  [OK] Docker is running")
        else:
            print("  [FAIL] Docker daemon is not running")
            ok = False
    else:
        print("  [FAIL] Docker CLI not found")
        ok = False

    if shutil.which("harbor"):
        print("  [OK] Harbor CLI is installed")
    else:
        print("  [FAIL] Harbor CLI not found")
        ok = False

    if os.environ.get("ANTHROPIC_API_KEY"):
        print("  [OK] ANTHROPIC_API_KEY is set")
    else:
        print("  [WARN] ANTHROPIC_API_KEY is not set")
        print("         The Claude Agent SDK requires an Anthropic API key.")
        ok = False

    # Check Claude Code CLI is installed (required by SDK)
    if shutil.which("claude"):
        print("  [OK] Claude Code CLI is installed")
    else:
        print("  [WARN] Claude Code CLI not found")
        print("         Install with: npm install -g @anthropic-ai/claude-code")
        print("         The SDK runs Claude Code as a subprocess.")

    print()
    return ok


def explain_claude_sdk() -> None:
    """Explain the Claude Agent SDK."""
    print("=" * 60)
    print("Step 2: Understanding the Claude Agent SDK")
    print("=" * 60)
    print()
    print("The Claude Agent SDK provides programmatic access to Claude Code.")
    print("Unlike the Langchain/LangGraph wrappers that build their own agent")
    print("loops, the SDK runs Claude Code as a subprocess:")
    print()
    print("  Your Python code")
    print("       |")
    print("  Claude Agent SDK (query() function)")
    print("       |")
    print("  Claude Code CLI (subprocess)")
    print("       |")
    print("  Anthropic API (Claude model)")
    print()
    print("Key features:")
    print("  - permission_mode='bypassPermissions' for unattended eval")
    print("  - MCP servers for custom tool routing")
    print("  - create_sdk_mcp_server() for in-process tools")
    print("  - Streaming message iteration")
    print("  - Cost tracking via ResultMessage")
    print()


def show_integration_pattern() -> None:
    """Show how the SDK integrates with Harbor."""
    print("=" * 60)
    print("Step 3: SDK-Harbor Integration Pattern")
    print("=" * 60)
    print()
    print("Challenge: The SDK runs Claude Code on the HOST, but Harbor")
    print("tasks execute inside CONTAINERS. We bridge this with MCP:")
    print()
    print("  1. Create an SDK MCP server with a 'container_exec' tool")
    print("  2. The tool calls environment.exec() to run commands")
    print("     inside the Harbor container")
    print("  3. Disable built-in tools so Claude only uses our tool")
    print("  4. Claude Code thinks it's running locally, but all")
    print("     commands execute in the container")
    print()
    print("  @tool('container_exec', 'Execute command in container',")
    print("        {'command': str})")
    print("  async def container_exec(args):")
    print("      result = await environment.exec(command=args['command'])")
    print("      return {'content': [{'type': 'text', 'text': result}]}")
    print()
    print("  server = create_sdk_mcp_server('harbor-env',")
    print("                                  tools=[container_exec])")
    print()


def run_evaluation() -> None:
    """Run the evaluation with the Claude SDK agent."""
    print("=" * 60)
    print("Step 4: Running Evaluation")
    print("=" * 60)
    print()

    task_path = LESSON_DIR / "tasks" / "coding-task"
    agent_path = "agent:ClaudeSDKHarborAgent"
    model = "anthropic/claude-sonnet-4-5-20250929"

    cmd = [
        "harbor", "run",
        "-p", str(task_path),
        "--agent", agent_path,
        "-m", model,
    ]

    print(f"Running: {' '.join(cmd)}")
    print()
    print("-" * 60)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(LESSON_DIR),
        env={**os.environ},
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    print("-" * 60)

    if result.returncode == 0:
        print("\nEvaluation completed!")
    else:
        print(f"\nEvaluation exited with code {result.returncode}")
    print()


def inspect_results() -> None:
    """Inspect evaluation results."""
    print("=" * 60)
    print("Step 5: Results")
    print("=" * 60)
    print()

    jobs_dir = LESSON_DIR / "jobs"
    if not jobs_dir.exists():
        print("  No jobs/ directory found.")
        return

    for result_file in sorted(jobs_dir.rglob("result.json")):
        try:
            data = json.loads(result_file.read_text())
            task_name = data.get("task", {}).get("name", "unknown")
            reward = data.get("reward", 0.0)
            print(f"  Task: {task_name}")
            print(f"  Reward: {reward}")
            duration = data.get("duration_sec")
            if duration is not None:
                print(f"  Duration: {duration:.1f}s")
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  Error reading results: {e}")

    print()


def show_summary() -> None:
    """Display lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("In this lesson you learned:")
    print("  - How the Claude Agent SDK runs Claude Code as a subprocess")
    print("  - How to use create_sdk_mcp_server() for in-process tools")
    print("  - How to route tool calls to Harbor's container environment")
    print("  - The permission_mode='bypassPermissions' setting for eval")
    print("  - Cost tracking via ResultMessage.total_cost_usd")
    print()
    print("Module 5 complete! You now know how to wrap and evaluate")
    print("agents from five different frameworks in Harbor:")
    print("  1. Claude Code (built-in)")
    print("  2. Langchain (ReAct agent)")
    print("  3. LangGraph (StateGraph)")
    print("  4. Deepagents (create_deep_agent)")
    print("  5. Claude Agent SDK (query + MCP)")
    print()
    print("Next module: Module 6 - Datasets & Benchmarks")


def main() -> None:
    """Run the claude-sdk-agent lesson."""
    print()
    print("########################################################")
    print("#  HARBOR TUTORIAL - Level 2, Module 5, Lesson 5       #")
    print("#  Claude Agent SDK in Harbor                          #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_claude_sdk()
    show_integration_pattern()
    run_evaluation()
    inspect_results()
    show_summary()


if __name__ == "__main__":
    main()
