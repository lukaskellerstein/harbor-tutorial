"""
Lesson 2: LangChain Agent in Harbor

Wrap a LangChain v1 create_agent() agent as a Harbor BaseAgent and evaluate
it against a coding task. The model is served by the LiteLLM proxy (Gemma 4).
"""

import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

LESSON_DIR = Path(__file__).parent

#: Alias defined in agent-eval-benchmark/infra/litellm/config.yaml (Gemma 4 26B).
MODEL = "gemma-large"


def litellm_root() -> str:
    """The LiteLLM gateway root URL (base URL without the /v1 suffix)."""
    base = os.environ.get("LITELLM_BASE_URL", "http://localhost:4000/v1")
    return base.removesuffix("/v1")


def check_prerequisites() -> bool:
    """Verify Docker, Harbor CLI, and the LiteLLM gateway."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
    print("=" * 60)

    ok = True

    if shutil.which("docker"):
        result = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, check=False
        )
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

    try:
        urllib.request.urlopen(f"{litellm_root()}/health/liveliness", timeout=5)
        print(f"  [OK] LiteLLM gateway is reachable at {litellm_root()}")
    except (urllib.error.URLError, OSError):
        print(f"  [FAIL] LiteLLM gateway is not reachable at {litellm_root()}")
        print("         Start the stack from agent-eval-benchmark:")
        print("             cd agent-eval-benchmark/infra && podman compose up -d")
        print(
            "         (for local models: lms server start && lms load google/gemma-4-e4b)"
        )
        ok = False

    print()
    return ok


def explain_wrapping() -> None:
    """Explain the concept of wrapping LangChain agents."""
    print("=" * 60)
    print("Step 2: Wrapping LangChain as a Harbor Agent")
    print("=" * 60)
    print()
    print("To evaluate a LangChain agent in Harbor, you extend BaseAgent:")
    print()
    print("  class LangchainHarborAgent(BaseAgent):")
    print("      async def run(self, instruction, environment, context):")
    print("          # Define tools that call environment.exec()")
    print("          # Hand them to create_agent() and await ainvoke()")
    print()
    print("LangChain v1's create_agent() owns the agent loop — reason, call")
    print("tools, observe, repeat — so the wrapper never writes one. What")
    print("you supply is the part Harbor cares about: a tool that reaches")
    print("into the task container.")
    print()


def show_agent_code() -> None:
    """Show the key parts of the agent wrapper."""
    print("=" * 60)
    print("Step 3: Agent Code Walkthrough")
    print("=" * 60)
    print()
    print("See agent.py for the full implementation. Key patterns:")
    print()
    print("  # An async tool awaits Harbor's async API directly:")
    print("  @tool")
    print("  async def execute_command(command: str) -> str:")
    print('      """Execute a shell command in the task container."""')
    print("      result = await environment.exec(command=command)")
    print("      return result.stdout or result.stderr or '(no output)'")
    print()
    print("  # create_agent() builds the ReAct loop for you:")
    print("  agent = create_agent(")
    print("      model=llm, tools=[execute_command], system_prompt=SYSTEM_PROMPT")
    print("  )")
    print("  await agent.ainvoke({'messages': [HumanMessage(content=instruction)]})")
    print()


def run_evaluation() -> None:
    """Run the Harbor evaluation with the LangChain agent."""
    print("=" * 60)
    print("Step 4: Running Evaluation")
    print("=" * 60)
    print()

    task_path = LESSON_DIR / "tasks" / "coding-task"
    agent_path = "agent:LangchainHarborAgent"

    cmd = [
        "harbor",
        "run",
        "-p",
        str(task_path),
        "--agent",
        agent_path,
        "-m",
        MODEL,
    ]

    print(f"Running: {' '.join(cmd)}")
    print()
    print("-" * 60)

    # PYTHONPATH makes `agent:LangchainHarborAgent` importable in the
    # harbor subprocess — cwd alone is not on its sys.path.
    env = {**os.environ, "PYTHONPATH": str(LESSON_DIR)}
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(LESSON_DIR),
        env=env,
        check=False,
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
    """Inspect evaluation results from the most recent job."""
    print("=" * 60)
    print("Step 5: Results")
    print("=" * 60)
    print()

    jobs_dir = LESSON_DIR / "jobs"
    job_dirs = (
        sorted(d for d in jobs_dir.glob("*") if d.is_dir()) if jobs_dir.exists() else []
    )
    if not job_dirs:
        print("  No jobs/ directory found.")
        return

    # Each job dir holds one result.json summarising the job, plus one per
    # trial in a subdirectory. The trial files carry the rewards.
    for result_file in sorted(job_dirs[-1].glob("*/result.json")):
        try:
            data = json.loads(result_file.read_text())
            rewards = (data.get("verifier_result") or {}).get("rewards") or {}

            print(f"  Task: {data.get('task_name', 'unknown')}")
            print(f"  Reward: {rewards.get('reward', 0.0)}")

            started, finished = data.get("started_at"), data.get("finished_at")
            if started and finished:
                duration = (
                    datetime.fromisoformat(finished) - datetime.fromisoformat(started)
                ).total_seconds()
                print(f"  Duration: {duration:.1f}s")

            if data.get("exception_info"):
                print(f"  Exception: {data['exception_info']}")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"  Error reading {result_file.name}: {e}")

    print()


def show_summary() -> None:
    """Display lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("In this lesson you learned:")
    print("  - How to wrap a LangChain agent as a Harbor BaseAgent")
    print("  - create_agent() (LangChain v1) supplies the ReAct loop, so the")
    print("    wrapper only defines tools and awaits ainvoke()")
    print("  - Async tools await environment.exec() directly — no bridging")
    print("  - Models route through the LiteLLM proxy (gemma-large = Gemma 4)")
    print("  - How to run the wrapped agent: --agent agent:ClassName")
    print()
    print("Next lesson: lesson-3-langgraph-agent (stateful graph agents in Harbor)")


def main() -> None:
    """Run the langchain-agent lesson."""
    print()
    print("########################################################")
    print("#  HARBOR TUTORIAL - Level 2, Module 5, Lesson 2       #")
    print("#  LangChain Agent in Harbor                           #")
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
