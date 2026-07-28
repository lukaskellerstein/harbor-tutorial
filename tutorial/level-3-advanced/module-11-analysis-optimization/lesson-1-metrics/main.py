"""
Lesson 1: Metrics & Aggregation

Harbor produces per-trial rewards (0 to 1). This lesson teaches you how to
aggregate those rewards into meaningful metrics -- mean, pass rate, pass@1,
and per-difficulty breakdowns -- to compare agents and track improvements.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from metrics_helpers import (
    compute_metrics,
    display_aggregate_metrics,
    display_grouped_by_difficulty,
    display_per_task_results,
    parse_trial_results,
)

LESSON_DIR = Path(__file__).parent
TASKS_DIR = LESSON_DIR / "tasks"
JOBS_DIR = LESSON_DIR / "jobs"


def check_prerequisites() -> bool:
    """Verify Docker and Harbor are available."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
    print("=" * 60)
    docker_ok = shutil.which("docker") is not None
    harbor_ok = shutil.which("harbor") is not None
    if docker_ok:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, text=True
        )
        docker_ok = result.returncode == 0
    print(f"  Docker:  {'[OK]' if docker_ok else '[FAIL] Docker daemon not running'}")
    print(f"  Harbor:  {'[OK]' if harbor_ok else '[FAIL] Install with: uv tool install harbor'}")
    print()
    if not (docker_ok and harbor_ok):
        print("Prerequisites not met. Please fix the issues above.")
        return False
    return True


def explain_metrics_concepts() -> None:
    """Explain the key metrics used in agent evaluation."""
    print("=" * 60)
    print("Step 2: Understanding Evaluation Metrics")
    print("=" * 60)
    print()
    print("Harbor's verifier assigns each trial a reward between 0 and 1:")
    print("  0.0 = failed | 0.5 = partial credit | 1.0 = perfect")
    print()
    print("Aggregate metrics computed from per-trial rewards:")
    print("  Mean reward -- average across all trials (primary metric)")
    print("  Max / Min   -- best and worst single-trial performance")
    print("  Pass rate   -- fraction with reward > 0 (any progress)")
    print("  Pass@1      -- fraction with reward == 1.0 (strict)")
    print()


def show_tasks() -> None:
    """Display the 4 tasks and their difficulties."""
    print("=" * 60)
    print("Step 3: Our Evaluation Tasks")
    print("=" * 60)
    print()
    tasks = [
        ("count-words", "easy", "Count words in a text file"),
        ("sort-numbers", "easy", "Sort numbers from a file"),
        ("csv-stats", "medium", "Compute stats from CSV (partial credit)"),
        ("matrix-multiply", "hard", "Multiply two matrices (partial credit)"),
    ]
    print(f"  {'Task':<22} {'Difficulty':<10}  Description")
    print(f"  {'-'*22} {'-'*10}  {'-'*38}")
    for name, diff, desc in tasks:
        print(f"  {name:<22} {diff:<10}  {desc}")
    print()


def run_evaluation() -> None:
    """Run all tasks with the oracle agent."""
    print("=" * 60)
    print("Step 4: Running the Evaluation")
    print("=" * 60)
    print()
    cmd = ["harbor", "run", "-p", str(TASKS_DIR), "-a", "oracle",
           "--delete", "-o", str(JOBS_DIR)]
    print(f"  Command: {' '.join(cmd)}")
    print()
    print("-" * 60)
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(LESSON_DIR),
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    print("-" * 60)
    status = "successfully" if result.returncode == 0 else f"with code {result.returncode}"
    print(f"Evaluation completed {status}!")
    print()


def analyze_results() -> None:
    """Parse results and compute aggregate metrics."""
    print("=" * 60)
    print("Step 5: Parsing Results")
    print("=" * 60)
    print()
    print("  result.json structure:")
    print('    verifier_result -> rewards -> {"reward": <0..1>}')
    print()
    trials = parse_trial_results(JOBS_DIR, TASKS_DIR)
    if not trials:
        print("  No trial results found. Try: harbor view jobs")
        return

    print()
    print("=" * 60)
    print("Step 6: Per-Task Results")
    print("=" * 60)
    print()
    display_per_task_results(trials)

    print("=" * 60)
    print("Step 7: Aggregate Metrics")
    print("=" * 60)
    print()
    display_aggregate_metrics(compute_metrics(trials))

    print("=" * 60)
    print("Step 8: Metrics Grouped by Difficulty")
    print("=" * 60)
    print()
    print("  Slicing results by task.toml metadata (difficulty):")
    print()
    display_grouped_by_difficulty(trials)


def explain_comparisons() -> None:
    """Explain how to compare across agents and models."""
    print("=" * 60)
    print("Step 9: Comparing Agents and Models")
    print("=" * 60)
    print()
    print("  Run the same dataset with different agents to compare:")
    print("    harbor run -p tasks -a oracle -o jobs/oracle")
    print("    harbor run -p tasks -a claude-code -m anthropic/claude-sonnet-4-5-20250929 -o jobs/claude")
    print("    harbor run -p tasks -a aider -m openai/gpt-4o -o jobs/aider")
    print()
    print("  Then compare mean reward, pass@1, and per-difficulty metrics.")
    print("  For interactive exploration: harbor view jobs")
    print()


def show_summary() -> None:
    """Display lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("  1. Rewards are per-trial scores from 0 (fail) to 1 (pass)")
    print("  2. Partial credit gives rewards between 0 and 1")
    print("  3. Mean reward is the primary aggregate metric")
    print("  4. Pass@1 measures strict correctness (reward == 1.0)")
    print("  5. Grouping by metadata reveals per-difficulty performance")
    print("  6. Use 'harbor view jobs' for interactive exploration")
    print()
    print("Next lesson: lesson-2-trajectories")
    print("  (Analyzing agent trajectories to understand HOW agents solve tasks)")


def main() -> None:
    """Run the metrics lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 3, Module 11         #")
    print("#          Lesson 1: Metrics & Aggregation              #")
    print("########################################################")
    print()
    if not check_prerequisites():
        sys.exit(1)
    explain_metrics_concepts()
    show_tasks()
    run_evaluation()
    analyze_results()
    explain_comparisons()
    show_summary()


if __name__ == "__main__":
    main()
