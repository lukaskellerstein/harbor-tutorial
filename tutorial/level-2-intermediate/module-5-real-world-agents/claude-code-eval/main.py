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
from pathlib import Path


LESSON_DIR = Path(__file__).parent


def check_prerequisites() -> bool:
    """Verify Docker, Harbor CLI, and ANTHROPIC_API_KEY are available."""
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

    # API key
    if os.environ.get("ANTHROPIC_API_KEY"):
        print("  [OK] ANTHROPIC_API_KEY is set")
    else:
        print("  [FAIL] ANTHROPIC_API_KEY is not set")
        print("         Export your key: export ANTHROPIC_API_KEY=sk-ant-...")
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

    result = subprocess.run(
        ["harbor", "run", "-c", "job.yaml"],
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

    # Look for trial results
    rewards: list[tuple[str, float]] = []
    for trial_dir in sorted(latest_job.rglob("result.json")):
        try:
            result_data = json.loads(trial_dir.read_text())
            task_name = result_data.get("task", {}).get("name", "unknown")
            reward = result_data.get("reward", 0.0)
            rewards.append((task_name, reward))
            print(f"  Task: {task_name}")
            print(f"    Reward: {reward}")
            duration = result_data.get("duration_sec")
            if duration is not None:
                print(f"    Duration: {duration:.1f}s")
            print()
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  Error reading {trial_dir}: {e}")

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
    print("  Agent trajectories are stored in each trial's logs/ directory.")
    print("  They show every tool call Claude Code made during the evaluation.")
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
    print("  - How ANTHROPIC_API_KEY is passed into the container via env")
    print("  - How to inspect results and agent trajectories in jobs/")
    print("  - How to view performance metrics (reward, duration)")
    print()
    print("Next lesson: langchain-agent (wrapping Langchain agents in Harbor)")


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
