"""
Harbor Tutorial — Level 3, Module 11, Lesson 4: Task Quality Analysis

Learn how to use `harbor check` to validate task quality against a rubric
and `harbor analyze` to inspect agent behavior in trial trajectories —
both powered by LLM-based evaluation.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

from helpers import (
    LESSON_DIR,
    QUALITY_TASK_DIR,
    TRIALS_DIR,
    explain_harbor_analyze,
    explain_harbor_check,
    show_analyze_command,
    show_check_output_format,
    show_custom_rubric,
    show_task_files,
)


def check_prerequisites() -> bool:
    """Verify Docker and Harbor are available."""
    print("=" * 60)
    print("PREREQUISITES CHECK")
    print("=" * 60)

    try:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            print("[ERROR] Docker is not running. Please start Docker first.")
            return False
        print("[OK] Docker is running")
    except FileNotFoundError:
        print("[ERROR] Docker is not installed.")
        return False

    try:
        result = subprocess.run(
            ["harbor", "--help"], capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            print("[ERROR] Harbor CLI returned an error.")
            return False
        print("[OK] Harbor CLI is available")
    except FileNotFoundError:
        print("[ERROR] Harbor is not installed. Run: uv tool install harbor")
        return False

    print()
    return True


def run_oracle_trial() -> str | None:
    """Run a trial with the oracle agent to generate trajectory data."""
    print("=" * 60)
    print("STEP 6: Running a Trial for Analysis")
    print("=" * 60)
    print()
    print("To demonstrate harbor analyze, we first need a completed trial.")
    print("We will run the oracle agent (which executes solution/solve.sh)")
    print("against our quality-task.")
    print()

    if TRIALS_DIR.exists():
        shutil.rmtree(TRIALS_DIR)

    cmd = [
        "harbor", "trial", "start",
        "-p", str(QUALITY_TASK_DIR),
        "-a", "oracle",
        "--delete",
        "--trials-dir", str(TRIALS_DIR),
    ]
    print(f"Running: {' '.join(cmd)}")
    print()

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=120, cwd=str(LESSON_DIR),
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        print(f"[ERROR] Trial failed with exit code {result.returncode}")
        return None

    if not TRIALS_DIR.exists():
        print("[ERROR] Trials directory was not created.")
        return None

    trial_dirs = [d for d in TRIALS_DIR.iterdir() if d.is_dir()]
    if not trial_dirs:
        print("[ERROR] No trial directory found.")
        return None

    trial_dir = str(trial_dirs[0])
    print(f"Trial output directory: {trial_dir}")
    print()

    # Show the trial result
    result_file = Path(trial_dir) / "result.json"
    if result_file.exists():
        data = json.loads(result_file.read_text())
        reward = data.get("verifier_result", {}).get("rewards", {})
        print(f"  Trial reward: {reward}")
        print()

    return trial_dir


def print_recap() -> None:
    """Summarize what was covered."""
    print("=" * 60)
    print("RECAP")
    print("=" * 60)
    print()
    print("In this lesson you learned about two LLM-powered quality tools:")
    print()
    print("  harbor check — validates task quality BEFORE running trials")
    print("    - Reads task files (instruction, tests, solution, Dockerfile)")
    print("    - Evaluates against a rubric (default: 11 criteria)")
    print("    - Custom rubrics use [[criteria]] with name, description, guidance")
    print("    - Default model: claude-sonnet-4-6")
    print("    - Output: check_report.json with pass/fail per criterion")
    print()
    print("  harbor analyze — inspects agent behavior AFTER trials complete")
    print("    - Reads agent trajectory, task definition, and results")
    print("    - Default rubric checks: reward_hacking, task_specification")
    print("    - Default model: claude-haiku-4-5")
    print("    - Output: analysis.json with summary and per-criterion results")
    print("    - Supports --passing / --failing filters")
    print()
    print("Together, these tools close the feedback loop:")
    print("  1. Write tasks -> harbor check -> fix quality issues")
    print("  2. Run trials -> harbor analyze -> detect reward hacking")
    print("  3. Iterate until tasks are robust and agents are honest")
    print()
    print("Next: Module 12 — Advanced Workflows (exec pipelines,")
    print("multi-container tasks, and Harbor Hub).")
    print()


def main() -> None:
    """Run all lesson steps."""
    print()
    print("=" * 60)
    print("  HARBOR TUTORIAL")
    print("  Level 3 | Module 11 | Lesson 4: Task Quality Analysis")
    print("=" * 60)
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_harbor_check()
    show_task_files()
    show_custom_rubric()
    show_check_output_format()
    explain_harbor_analyze()

    trial_dir = run_oracle_trial()
    show_analyze_command(trial_dir)
    print_recap()


if __name__ == "__main__":
    main()
