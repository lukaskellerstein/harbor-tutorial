"""
Lesson: Running a Single Trial
==============================
Learn how to run a single agent attempt at a task using `harbor trial start`,
inspect the results, and understand the difference between trials and jobs.
"""

import json
import sys
from pathlib import Path

from helpers import check_prerequisites, find_latest_trial, run_harbor_command


def show_task_structure() -> None:
    """Display the task directory we will run against."""
    print("=" * 60)
    print("Step 1: Understanding the task")
    print("=" * 60)
    task_dir = Path("tasks/hello-task")
    print(f"\nTask directory: {task_dir}\n")
    print("Directory structure:")
    print("  tasks/hello-task/")
    print("  ├── instruction.md      # What the agent must do")
    print("  ├── task.toml           # Task configuration & metadata")
    print("  ├── environment/")
    print("  │   └── Dockerfile      # Container the agent runs in")
    print("  ├── solution/")
    print("  │   └── solve.sh        # Reference solution (used by oracle)")
    print("  └── tests/")
    print("      └── test.sh         # Verifier that produces a reward (0-1)")
    instruction = (task_dir / "instruction.md").read_text().strip()
    print(f"\nInstruction: {instruction}\n")


def explain_trial_vs_job() -> None:
    """Explain the difference between trial start and run."""
    print("=" * 60)
    print("Step 2: Trial vs. Job")
    print("=" * 60)
    print("\nHarbor has two ways to run evaluations:\n")
    print("  harbor trial start   - Runs a SINGLE trial (one agent, one task)")
    print("                         Results go to ./trials/ by default")
    print("                         Great for testing and debugging\n")
    print("  harbor run           - Runs a JOB (multiple trials)")
    print("                         Supports concurrency, retries, multiple agents")
    print("                         Results go to ./jobs/ by default")
    print("                         Configured via job.yaml or CLI flags\n")


def run_single_trial() -> Path | None:
    """Run a single trial using the oracle agent."""
    print("=" * 60)
    print("Step 3: Running a single trial with `harbor trial start`")
    print("=" * 60)
    print()

    cmd = [
        "harbor",
        "trial",
        "start",
        "-p",
        "tasks/hello-task",
        "-a",
        "oracle",
        "--delete",
    ]

    print("This command does the following:")
    print("  -p tasks/hello-task   Use our local task directory")
    print("  -a oracle             Use the oracle agent (runs solution/solve.sh)")
    print("  --delete              Remove the Docker container after completion\n")
    print("Running trial (this may take a minute on first run)...")
    print("-" * 60)

    result = run_harbor_command(cmd)

    print("-" * 60)

    if result.returncode != 0:
        print(f"Trial failed with exit code {result.returncode}")
        return None

    trial_dir = find_latest_trial()
    if trial_dir:
        print(f"\nTrial output directory: {trial_dir}\n")
    return trial_dir


def inspect_trial_results(trial_dir: Path) -> None:
    """Read and display the trial's result files."""
    print("=" * 60)
    print("Step 4: Inspecting the trial results")
    print("=" * 60)

    # List files
    print(f"\nContents of {trial_dir}/:")
    for item in sorted(trial_dir.rglob("*")):
        if item.is_file():
            print(f"  {item.relative_to(trial_dir)}")

    # Read result.json
    result_path = trial_dir / "result.json"
    if result_path.exists():
        print("\n--- result.json (key fields) ---")
        data = json.loads(result_path.read_text())
        print(f"  trial_name:  {data.get('trial_name', 'N/A')}")
        print(f"  task_name:   {data.get('task_name', 'N/A')}")
        agent = data.get("agent_info", {})
        print(f"  agent:       {agent.get('name', 'N/A')} v{agent.get('version', 'N/A')}")
        rewards = data.get("verifier_result", {}).get("rewards", [])
        print(f"  rewards:     {rewards}")
        exc = data.get("exception_info")
        if exc:
            print(f"  exception:   {exc.get('exception_type')}: {exc.get('exception_message')}")
        else:
            print("  exception:   None (success)")

    # Read reward.txt
    reward_path = trial_dir / "verifier" / "reward.txt"
    if reward_path.exists():
        reward = reward_path.read_text().strip()
        print("\n--- verifier/reward.txt ---")
        print(f"  Reward: {reward}")
        if float(reward) == 1.0:
            print("  The oracle agent solved the task perfectly!")
        else:
            print(f"  Reward was {reward} (expected 1.0 for oracle)")
    print()


def recap() -> None:
    """Summarize what was learned."""
    print("=" * 60)
    print("Recap")
    print("=" * 60)
    print("\nIn this lesson you learned:\n")
    print("  1. `harbor trial start` runs a single agent attempt at a task")
    print("  2. The oracle agent runs solution/solve.sh to validate tasks")
    print("  3. Results are stored in ./trials/<trial-name>/")
    print("  4. result.json contains trial metadata, agent info, and rewards")
    print("  5. verifier/reward.txt contains the numeric reward (0 to 1)")
    print("  6. Use `harbor trial start` for single trials; `harbor run` for jobs")
    print("\nNext lesson: Job Configuration with job.yaml\n")


def main() -> None:
    """Run the single-trial lesson."""
    print()
    print("=" * 60)
    print("  Harbor Tutorial - Module 3, Lesson 1")
    print("  Running a Single Trial")
    print("=" * 60)
    print()

    if not check_prerequisites():
        sys.exit(1)

    show_task_structure()
    explain_trial_vs_job()

    trial_dir = run_single_trial()
    if trial_dir is None:
        print("Could not complete the trial. Check the errors above.")
        sys.exit(1)

    inspect_trial_results(trial_dir)
    recap()


if __name__ == "__main__":
    main()
