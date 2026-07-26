"""
Lesson 2: Langchain Agent in Harbor

Wrap a Langchain ReAct agent as a Harbor BaseAgent and evaluate it
against coding tasks. Demonstrates bridging sync Langchain tools
with async Harbor environment operations.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


LESSON_DIR = Path(__file__).parent


def check_prerequisites() -> bool:
    """Verify Docker, Harbor CLI, and API keys are available."""
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
        print("         The Langchain agent uses OpenAI models by default.")
        print("         Set it with: export OPENAI_API_KEY=sk-...")
        ok = False

    print()
    return ok


def explain_wrapping() -> None:
    """Explain the concept of wrapping Langchain agents."""
    print("=" * 60)
    print("Step 2: Wrapping Langchain as a Harbor Agent")
    print("=" * 60)
    print()
    print("To evaluate a Langchain agent in Harbor, you extend BaseAgent:")
    print()
    print("  class LangchainHarborAgent(BaseAgent):")
    print("      async def run(self, instruction, environment, context):")
    print("          # Create Langchain tools that call environment.exec()")
    print("          # Build and run the agent loop")
    print()
    print("The key challenge: Langchain tools are synchronous, but Harbor's")
    print("environment.exec() is async. We solve this with:")
    print()
    print("  1. Get the running asyncio event loop")
    print("  2. Use asyncio.run_coroutine_threadsafe() to schedule async")
    print("     Harbor calls from sync Langchain tool callbacks")
    print("  3. Use asyncio.to_thread() to run sync Langchain calls")
    print("     without blocking the async event loop")
    print()


def show_agent_code() -> None:
    """Show the key parts of the agent wrapper."""
    print("=" * 60)
    print("Step 3: Agent Code Walkthrough")
    print("=" * 60)
    print()
    print("See agent.py for the full implementation. Key patterns:")
    print()
    print("  # Bridge async Harbor calls into sync Langchain tools:")
    print("  loop = asyncio.get_running_loop()")
    print("  def run_async_in_thread(coro):")
    print("      future = asyncio.run_coroutine_threadsafe(coro, loop)")
    print("      return future.result(timeout=120)")
    print()
    print("  @langchain_tool")
    print("  def execute_command(command: str) -> str:")
    print("      result = run_async_in_thread(environment.exec(command=command))")
    print("      return result.stdout or result.stderr or ''")
    print()
    print("  # Simple agent loop: LLM -> tool calls -> results -> repeat")
    print("  for i in range(max_iterations):")
    print("      response = llm_with_tools.invoke(messages)")
    print("      if not response.tool_calls: break")
    print("      # Execute tools and append results...")
    print()


def run_evaluation() -> None:
    """Run the Harbor evaluation with the Langchain agent."""
    print("=" * 60)
    print("Step 4: Running Evaluation")
    print("=" * 60)
    print()

    task_path = LESSON_DIR / "tasks" / "coding-task"
    agent_path = "agent:LangchainHarborAgent"
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
    print("  - How to wrap a Langchain agent as a Harbor BaseAgent")
    print("  - The async/sync bridging challenge between frameworks")
    print("  - How to create Langchain tools that call environment.exec()")
    print("  - How to run the wrapped agent: --agent agent:ClassName")
    print()
    print("Next lesson: langgraph-agent (stateful graph agents in Harbor)")


def main() -> None:
    """Run the langchain-agent lesson."""
    print()
    print("########################################################")
    print("#  HARBOR TUTORIAL - Level 2, Module 5, Lesson 2       #")
    print("#  Langchain Agent in Harbor                           #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_wrapping()
    show_agent_code()
    run_evaluation()
    inspect_results()
    show_summary()


if __name__ == "__main__":
    main()
