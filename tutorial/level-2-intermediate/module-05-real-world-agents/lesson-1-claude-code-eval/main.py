"""
Lesson 1: Evaluating Claude Code

Run the built-in claude-code agent against custom tasks.
Claude Code is a built-in Harbor agent — no wrapping required.
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv


LESSON_DIR = Path(__file__).parent

# Credentials live in this lesson's .env file (git-ignored), not in the global
# shell profile. load_dotenv understands the `export KEY=value` syntax used
# there, and puts the token in os.environ so the harbor subprocess inherits it.
load_dotenv(LESSON_DIR / ".env")


def check_prerequisites() -> bool:
    """Verify Docker, Harbor CLI, and Anthropic credentials are available."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
    print("=" * 60)

    ok = True

    # Docker
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

    # Harbor
    if shutil.which("harbor"):
        print("  [OK] Harbor CLI is installed")
    else:
        print("  [FAIL] Harbor CLI not found. Install with: uv tool install harbor")
        ok = False

    # Anthropic credentials: subscription token (preferred) or API key
    oauth_token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if oauth_token:
        print("  [OK] CLAUDE_CODE_OAUTH_TOKEN loaded (Claude subscription auth)")
        if api_key:
            print("       ANTHROPIC_API_KEY is also set; CLAUDE_FORCE_OAUTH=1 will")
            print("       be passed to Harbor so the subscription token wins.")
    elif api_key:
        print("  [OK] ANTHROPIC_API_KEY is set (API billing)")
        print("       To bill your Claude subscription instead, run `claude setup-token`")
        print("       and put CLAUDE_CODE_OAUTH_TOKEN in .env")
    else:
        print("  [FAIL] No Anthropic credentials found")
        print(f"         Expected a .env file at: {LESSON_DIR / '.env'}")
        print("         Subscription: claude setup-token, then add to .env:")
        print("           export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...")
        print("         API key alternative:")
        print("           export ANTHROPIC_API_KEY=sk-ant-...")
        ok = False

    print()
    return ok


def explain_builtin_agent() -> None:
    """Explain that claude-code is a built-in Harbor agent."""
    print("=" * 60)
    print("Step 2: Understanding the Built-in Claude Code Agent")
    print("=" * 60)
    print()
    print("Claude Code is one of Harbor's 37+ built-in agents.")
    print("Unlike custom agents, you do NOT need to write any wrapper code.")
    print()
    print("How it works:")
    print("  1. Harbor installs Claude Code inside the task container")
    print("  2. The agent receives the task instruction")
    print("  3. Claude Code uses its tools (Bash, Read, Edit, etc.) to solve the task")
    print("  4. Harbor runs the verifier test script and records the reward")
    print()
    print("To use it, simply specify: -a claude-code")
    print("Or in job.yaml:  agents: [{name: claude-code}]")
    print()


def show_tasks() -> None:
    """Display the tasks that will be evaluated."""
    print("=" * 60)
    print("Step 3: Tasks Overview")
    print("=" * 60)
    print()

    tasks_dir = LESSON_DIR / "tasks"
    for task_dir in sorted(tasks_dir.iterdir()):
        if not task_dir.is_dir():
            continue
        instruction_file = task_dir / "instruction.md"
        if instruction_file.exists():
            print(f"  Task: {task_dir.name}")
            instruction = instruction_file.read_text().strip()
            for line in instruction.split("\n"):
                print(f"    {line}")
            print()


def run_evaluation() -> None:
    """Run the Harbor evaluation using the job.yaml config."""
    print("=" * 60)
    print("Step 4: Running Evaluation with Claude Code")
    print("=" * 60)
    print()
    print("Running: harbor run -c job.yaml")
    print("This will evaluate Claude Code against all tasks in tasks/")
    print()
    print("-" * 60)

    env = {**os.environ}
    if env.get("CLAUDE_CODE_OAUTH_TOKEN"):
        # Harbor's claude-code agent injects CLAUDE_CODE_OAUTH_TOKEN into the
        # container by itself; CLAUDE_FORCE_OAUTH drops any API key so the CLI
        # bills the Claude subscription instead of the API.
        env.setdefault("CLAUDE_FORCE_OAUTH", "1")

    result = subprocess.run(
        ["harbor", "run", "-c", "job.yaml"],
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
        print("\nEvaluation completed successfully!")
    else:
        print(f"\nEvaluation exited with code {result.returncode}")
    print()


def inspect_results() -> None:
    """Inspect the jobs/ directory for results and trajectories."""
    print("=" * 60)
    print("Step 5: Inspecting Results and Trajectories")
    print("=" * 60)
    print()

    jobs_dir = LESSON_DIR / "jobs"
    if not jobs_dir.exists():
        print("  No jobs/ directory found. The evaluation may not have run.")
        return

    # Find the most recent job directory
    job_dirs = sorted(jobs_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    if not job_dirs:
        print("  No job results found.")
        return

    latest_job = job_dirs[0]
    print(f"  Latest job: {latest_job.name}")
    print()

    # One result.json per trial, plus a job-level summary at the job root.
    # Only per-trial files carry "task_name", so that key also filters out
    # the job-level file (which has no task and no reward).
    rewards: list[tuple[str, float]] = []
    for result_file in sorted(latest_job.rglob("result.json")):
        try:
            data = json.loads(result_file.read_text())
        except json.JSONDecodeError as e:
            print(f"  Error reading {result_file}: {e}")
            continue

        task_name = data.get("task_name")
        if task_name is None:
            continue  # job-level summary, not a trial

        trial_dir = result_file.parent

        # Reward lives under verifier_result.rewards.reward, and is absent
        # entirely when the trial raised before verification.
        verifier_result = data.get("verifier_result") or {}
        reward = (verifier_result.get("rewards") or {}).get("reward")

        print(f"  Task: {task_name}")

        exception_info = data.get("exception_info")
        if exception_info:
            # The trial never reached the verifier -- this is the failure
            # message you actually need, so print it instead of a bare 0.0.
            print(f"    FAILED: {exception_info.get('exception_type')}")
            print(f"    {exception_info.get('exception_message')}")
            print(f"    Full traceback: {trial_dir / 'exception.txt'}")
            print(f"    Trial log:      {trial_dir / 'trial.log'}")
        else:
            reward = 0.0 if reward is None else reward
            rewards.append((task_name, reward))
            print(f"    Reward: {reward}")
            if reward < 1.0:
                # Verifier ran and rejected the work -- its stdout says why.
                print(f"    Verifier output: {trial_dir / 'verifier' / 'test-stdout.txt'}")
                print(f"    Agent transcript: {trial_dir / 'agent' / 'claude-code.txt'}")

        started, finished = data.get("started_at"), data.get("finished_at")
        if started and finished:
            elapsed = datetime.fromisoformat(finished) - datetime.fromisoformat(started)
            print(f"    Duration: {elapsed.total_seconds():.1f}s")
        print()

    if rewards:
        avg_reward = sum(r for _, r in rewards) / len(rewards)
        print(f"  Average reward: {avg_reward:.2f}")
        print(f"  Tasks passed: {sum(1 for _, r in rewards if r >= 1.0)}/{len(rewards)}")
    else:
        print("  No trial results found yet.")
        print("  Check the jobs/ directory manually after the evaluation completes.")

    print()
    print("  To explore results interactively, run:")
    print("    harbor view jobs")
    print()
    print("  Each trial directory under jobs/<timestamp>/ contains:")
    print("    exception.txt          - traceback, only if the trial crashed")
    print("    trial.log              - Harbor's step-by-step log for the trial")
    print("    agent/claude-code.txt  - every tool call the agent made")
    print("    verifier/test-stdout.txt - why the verifier gave that reward")
    print()


def show_summary() -> None:
    """Display a summary of what was learned."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("In this lesson you learned:")
    print("  - Claude Code is a built-in Harbor agent (no wrapping needed)")
    print("  - How to configure a job.yaml for Claude Code evaluations")
    print("  - How auth (CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY) is")
    print("    injected into the container by the claude-code agent at runtime")
    print("  - How to inspect results and agent trajectories in jobs/")
    print("  - How to view performance metrics (reward, duration)")
    print()
    print("Next lesson: lesson-2-langchain-agent (wrapping Langchain agents in Harbor)")


def main() -> None:
    """Run the claude-code-eval lesson."""
    print()
    print("########################################################")
    print("#  HARBOR TUTORIAL - Level 2, Module 5, Lesson 1       #")
    print("#  Evaluating Claude Code                              #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_builtin_agent()
    show_tasks()
    run_evaluation()
    inspect_results()
    show_summary()


if __name__ == "__main__":
    main()
