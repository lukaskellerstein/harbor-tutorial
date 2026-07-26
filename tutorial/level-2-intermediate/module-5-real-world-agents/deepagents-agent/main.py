"""
Lesson 4: Deepagents in Harbor

Wrap a Deepagents framework agent as a Harbor BaseAgent.
Deepagents provides built-in tools for filesystem operations,
memory, and subagent orchestration on top of LangGraph.
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

    if os.environ.get("OPENAI_API_KEY"):
        print("  [OK] OPENAI_API_KEY is set")
    else:
        print("  [WARN] OPENAI_API_KEY is not set")
        ok = False

    print()
    return ok


def explain_deepagents() -> None:
    """Explain the Deepagents framework."""
    print("=" * 60)
    print("Step 2: Understanding Deepagents")
    print("=" * 60)
    print()
    print("Deepagents (by LangChain) is a higher-level framework built")
    print("on LangGraph. It provides:")
    print()
    print("  - create_deep_agent(): one-call agent creation with middleware")
    print("  - FilesystemMiddleware: built-in file read/write tools")
    print("  - MemoryMiddleware: persistent memory across turns")
    print("  - SubAgentMiddleware: spawn and manage sub-agents")
    print("  - RubricMiddleware: structured evaluation of agent outputs")
    print()
    print("For Harbor integration, we map Deepagents' built-in tools")
    print("to Harbor's environment.exec() API, so all file operations")
    print("happen inside the task container rather than on the host.")
    print()


def show_tool_mapping() -> None:
    """Show how Deepagents tools map to Harbor's environment."""
    print("=" * 60)
    print("Step 3: Tool Mapping Strategy")
    print("=" * 60)
    print()
    print("  Deepagents built-in      Harbor equivalent")
    print("  --------------------     -----------------")
    print("  write_file(path, data)   environment.exec('cat > path ...')")
    print("  read_file(path)          environment.exec('cat path')")
    print("  execute(command)         environment.exec(command)")
    print()
    print("  By creating custom Langchain tools that call environment.exec(),")
    print("  we route all operations through Harbor's container, keeping the")
    print("  agent's behavior identical to running in a real environment.")
    print()


def run_evaluation() -> None:
    """Run the evaluation with the Deepagents agent."""
    print("=" * 60)
    print("Step 4: Running Evaluation")
    print("=" * 60)
    print()

    task_path = LESSON_DIR / "tasks" / "file-task"
    agent_path = "agent:DeepagentsHarborAgent"
    model = "openai/gpt-4o"

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
    print("  - What Deepagents provides beyond raw LangGraph")
    print("  - How to map Deepagents' built-in tools to Harbor's environment")
    print("  - The fallback pattern for graceful degradation")
    print("  - How higher-level frameworks simplify agent creation")
    print()
    print("Next lesson: claude-sdk-agent (Claude Agent SDK in Harbor)")


def main() -> None:
    """Run the deepagents-agent lesson."""
    print()
    print("########################################################")
    print("#  HARBOR TUTORIAL - Level 2, Module 5, Lesson 4       #")
    print("#  Deepagents in Harbor                                #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_deepagents()
    show_tool_mapping()
    run_evaluation()
    inspect_results()
    show_summary()


if __name__ == "__main__":
    main()
