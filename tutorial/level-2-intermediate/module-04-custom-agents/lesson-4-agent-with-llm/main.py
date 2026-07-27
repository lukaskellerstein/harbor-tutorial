"""
Lesson 4: LLM-Powered Custom Agent

Learn how to build a custom Harbor agent that uses a language model
to reason about tasks and generate solutions. The model is served by the
LiteLLM proxy (Gemma 4).
"""

import os
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path


LESSON_DIR = Path(__file__).parent

#: Alias defined in agent-eval-benchmark/infra/litellm/config.yaml (Gemma 4 26B).
MODEL = "gemma-large"


def litellm_root() -> str:
    """The LiteLLM gateway root URL (base URL without the /v1 suffix)."""
    base = os.environ.get("LITELLM_BASE_URL", "http://localhost:4000/v1")
    return base[: -len("/v1")] if base.endswith("/v1") else base


def show_concept() -> None:
    """Explain the LLM-powered agent concept."""
    print("=" * 60)
    print("Step 1: The Agent-LLM-Environment Loop")
    print("=" * 60)
    print()
    print("  Custom agents can integrate LLMs for reasoning about tasks.")
    print("  Instead of hard-coding solutions, the agent asks an LLM to")
    print("  generate commands, then executes them in the container.")
    print()
    print("  Key concepts:")
    print("  - self.model_name: receives the -m flag from the CLI")
    print("  - LiteLLM: unified interface to all model providers, reached")
    print(f"    here through the local proxy at {litellm_root()}")
    print("  - Iterative refinement: ask -> execute -> check -> retry")
    print()


def show_loop_diagram() -> None:
    """Display the agent-LLM-environment loop diagram."""
    print("=" * 60)
    print("Step 2: The Loop Pattern")
    print("=" * 60)
    print()
    print("    Agent                    LLM                  Container")
    print("      |                       |                       |")
    print("      |--- instruction ------>|                       |")
    print("      |<-- bash commands -----|                       |")
    print("      |                       |                       |")
    print("      |--- exec commands ---------------------------->|")
    print("      |<-- result (stdout/stderr) -------------------|")
    print("      |                       |                       |")
    print("      |   [if error]          |                       |")
    print("      |--- error + context -->|                       |")
    print("      |<-- fixed commands ----|                       |")
    print("      |--- exec commands ---------------------------->|")
    print("      |<-- result -----------------------------------|")
    print("      |                       |                       |")
    print()
    print("  The loop repeats up to 3 times until success or max retries.")
    print()


def show_agent_code() -> None:
    """Display the agent implementation."""
    print("=" * 60)
    print("Step 3: The LLM Agent Code")
    print("=" * 60)

    agent_path = LESSON_DIR / "agent.py"
    if agent_path.exists():
        content = agent_path.read_text()
        print(f"\n  File: agent.py\n")
        for line in content.splitlines():
            print(f"    {line}")
    print()


def show_task() -> None:
    """Show the task that the agent will solve."""
    print("=" * 60)
    print("Step 4: The Task")
    print("=" * 60)

    instruction_path = LESSON_DIR / "tasks" / "llm-task" / "instruction.md"
    if instruction_path.exists():
        content = instruction_path.read_text()
        print(f"\n  File: tasks/llm-task/instruction.md\n")
        for line in content.splitlines():
            print(f"    {line}")
    print()


def explain_running() -> None:
    """Explain how to run the agent with different models."""
    print("=" * 60)
    print("Step 5: Running the LLM Agent")
    print("=" * 60)
    print()
    print("  Command:")
    print("    harbor run -p tasks/llm-task \\")
    print("      --agent agent:LLMAgent \\")
    print(f"      -m {MODEL}")
    print()
    print("  The -m flag sets self.model_name on the agent. It carries a")
    print("  LiteLLM gateway ALIAS, not a provider model id. The aliases are")
    print("  defined in agent-eval-benchmark/infra/litellm/config.yaml:")
    print()
    print("    gemma-large    Gemma 4 26B MoE via OpenRouter  (default here)")
    print("    gemma-small    Gemma 4 E4B via LMStudio        (local, offline)")
    print("    gemma-local    same as gemma-small")
    print("    frontier       hosted frontier model")
    print()
    print("  No provider API key is needed — the proxy holds the keys and")
    print("  swapping providers is a config change, never a code change.")
    print()


def check_prerequisites() -> bool:
    """Verify Docker and the LiteLLM gateway are available."""
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

    try:
        urllib.request.urlopen(f"{litellm_root()}/health/liveliness", timeout=5)
        print(f"  [OK] LiteLLM gateway is reachable at {litellm_root()}")
    except (urllib.error.URLError, OSError):
        print(f"  [FAIL] LiteLLM gateway is not reachable at {litellm_root()}")
        print("         Start the stack from agent-eval-benchmark:")
        print("             cd agent-eval-benchmark/infra && podman compose up -d")
        print("         (for local aliases: lms server start && lms load google/gemma-4-e4b)")
        ok = False

    return ok


def run_evaluation() -> None:
    """Run the evaluation if Docker and the gateway are available."""
    print("=" * 60)
    print("Step 6: Running the Evaluation")
    print("=" * 60)
    print()

    if not check_prerequisites():
        print()
        print("  Prerequisites missing — skipping evaluation run.")
        print()
        return

    print()
    task_path = LESSON_DIR / "tasks" / "llm-task"

    cmd = [
        "harbor", "run",
        "-p", str(task_path),
        "--agent", "agent:LLMAgent",
        "-m", MODEL,
    ]

    print(f"  Running: {' '.join(cmd)}")
    print()
    print("-" * 60)

    # PYTHONPATH makes `agent:LLMAgent` importable in the harbor subprocess —
    # cwd alone is not on its sys.path.
    env = {**os.environ, "PYTHONPATH": str(LESSON_DIR)}
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(LESSON_DIR),
        env=env,
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    print("-" * 60)

    if result.returncode == 0:
        print("\n  Evaluation completed successfully!")
    else:
        print(f"\n  Evaluation finished with return code {result.returncode}")
    print()


def show_summary() -> None:
    """Display lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("  Key takeaways:")
    print("  - LLM-powered agents use language models for reasoning")
    print("  - The agent-LLM-environment loop: ask -> execute -> check -> retry")
    print("  - self.model_name receives the -m flag from the harbor CLI")
    print("  - The LiteLLM proxy serves the model behind a friendly alias,")
    print("    so switching providers never touches the agent code")
    print("  - Iterative refinement with error feedback improves success rates")
    print()
    print("  You have completed Module 4: Building Custom Agents!")
    print()
    print("  Next: Module 5 - Evaluating Real-World Agents")
    print("  Learn to evaluate Claude Code, Langchain, Langgraph, and more.")


def main() -> None:
    """Run the agent-with-llm lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Module 4, Lesson 4         #")
    print("#     LLM-Powered Custom Agent                         #")
    print("########################################################")
    print()

    show_concept()
    show_loop_diagram()
    show_agent_code()
    show_task()
    explain_running()
    run_evaluation()
    show_summary()


if __name__ == "__main__":
    main()
