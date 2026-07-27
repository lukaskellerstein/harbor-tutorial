"""
Lesson 4: Deepagents in Harbor

Wrap a Deepagents framework agent as a Harbor BaseAgent.
Deepagents is batteries-included: planning, filesystem tools, shell
execution, and subagent orchestration ship with create_deep_agent().
The model is served by the LiteLLM proxy (Gemma 4).
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

    try:
        urllib.request.urlopen(f"{litellm_root()}/health/liveliness", timeout=5)
        print(f"  [OK] LiteLLM gateway is reachable at {litellm_root()}")
    except (urllib.error.URLError, OSError):
        print(f"  [FAIL] LiteLLM gateway is not reachable at {litellm_root()}")
        print("         Start the stack from agent-eval-benchmark:")
        print("             cd agent-eval-benchmark/infra && podman compose up -d")
        print("         (for local models: lms server start && lms load google/gemma-4-e4b)")
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
    print("on LangGraph — and it is batteries-included. create_deep_agent()")
    print("ships with these tools out of the box:")
    print()
    print("  - write_todos: plan and track multi-step work")
    print("  - ls, read_file, write_file, edit_file, glob, grep: file ops")
    print("  - execute: run shell commands")
    print("  - task: delegate to sub-agents")
    print()
    print("We do NOT define any of these tools ourselves. The only thing")
    print("we supply is a *backend* that tells the built-in tools where")
    print("to operate: inside Harbor's task container.")
    print()


def show_backend_mapping() -> None:
    """Show how the deepagents backend bridges to Harbor's environment."""
    print("=" * 60)
    print("Step 3: Backend Strategy")
    print("=" * 60)
    print()
    print("  Deepagents' BaseSandbox derives ALL built-in tools from three")
    print("  primitives. We implement just those against Harbor:")
    print()
    print("  Backend primitive       Harbor equivalent")
    print("  -----------------       -----------------")
    print("  execute(command)        environment.exec(command)")
    print("  upload_files(...)       environment.exec('... base64 -d > path')")
    print("  download_files(...)     environment.exec('base64 < path')")
    print()
    print("  Every built-in tool (read_file, write_file, edit_file, ls,")
    print("  glob, grep, execute) then automatically operates inside the")
    print("  task container — zero custom tool definitions.")
    print()


def run_evaluation() -> None:
    """Run the evaluation with the Deepagents agent."""
    print("=" * 60)
    print("Step 4: Running Evaluation")
    print("=" * 60)
    print()

    task_path = LESSON_DIR / "tasks" / "file-task"
    agent_path = "agent:DeepagentsHarborAgent"

    cmd = [
        "harbor", "run",
        "-p", str(task_path),
        "--agent", agent_path,
        "-m", MODEL,
    ]

    print(f"Running: {' '.join(cmd)}")
    print()
    print("-" * 60)

    # PYTHONPATH makes `agent:DeepagentsHarborAgent` importable in the
    # harbor subprocess — cwd alone is not on its sys.path.
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
        print("\nEvaluation completed!")
    else:
        print(f"\nEvaluation exited with code {result.returncode}")
    print()


def trial_duration_sec(data: dict) -> float | None:
    """Wall-clock seconds for a trial, derived from its start/finish stamps."""
    started, finished = data.get("started_at"), data.get("finished_at")
    if not started or not finished:
        return None
    return (
        datetime.fromisoformat(finished) - datetime.fromisoformat(started)
    ).total_seconds()


def inspect_results() -> None:
    """Inspect the results of the most recent job.

    Only trial-level result.json files carry per-task data; the job-level one
    next to them holds aggregate stats, so it is skipped here.
    """
    print("=" * 60)
    print("Step 5: Results")
    print("=" * 60)
    print()

    jobs_dir = LESSON_DIR / "jobs"
    job_dirs = sorted(d for d in jobs_dir.glob("*") if d.is_dir())
    if not job_dirs:
        print("  No job runs found under jobs/.")
        return

    # Job directories are timestamp-named, so the last one is the newest.
    latest = job_dirs[-1]
    print(f"  Job: {latest.name}")
    if len(job_dirs) > 1:
        print(f"  ({len(job_dirs) - 1} older run(s) in jobs/ not shown)")
    print()

    result_files = sorted(latest.glob("*/result.json"))
    if not result_files:
        print("  No trial results — the job failed before any trial finished.")
        print(f"  See {latest / 'job.log'} for the cause.")
        return

    for result_file in result_files:
        try:
            data = json.loads(result_file.read_text())
        except json.JSONDecodeError as e:
            print(f"  Error reading {result_file.name}: {e}")
            continue

        rewards = (data.get("verifier_result") or {}).get("rewards") or {}
        reward = rewards.get("reward")

        print(f"  Task: {data.get('task_name', 'unknown')}")
        print(f"  Reward: {reward if reward is not None else 'n/a'}")

        duration = trial_duration_sec(data)
        if duration is not None:
            print(f"  Duration: {duration:.1f}s")

        exception_info = data.get("exception_info")
        if exception_info:
            print(f"  Exception: {exception_info}")
        print()


def show_summary() -> None:
    """Display lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("In this lesson you learned:")
    print("  - Deepagents is batteries-included: planning, file ops, execute,")
    print("    and sub-agents ship with create_deep_agent()")
    print("  - Backends, not tools, are the integration point: BaseSandbox")
    print("    derives every built-in tool from execute/upload/download")
    print("  - Models route through the LiteLLM proxy (gemma-large = Gemma 4)")
    print()
    print("Next lesson: lesson-5-claude-sdk-agent (Claude Agent SDK in Harbor)")


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
    show_backend_mapping()
    run_evaluation()
    inspect_results()
    show_summary()


if __name__ == "__main__":
    main()
