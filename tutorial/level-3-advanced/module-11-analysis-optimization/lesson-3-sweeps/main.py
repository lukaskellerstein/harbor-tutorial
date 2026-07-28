"""
Harbor Tutorial — Module 11, Lesson 3: Configuration Sweeps

Learn how to use `harbor sweeps run` to systematically explore agent/model
configurations by running iterative sweep rounds that drop successful tasks
and focus compute on the hardest problems.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

from explanations import (
    explain_cli_flags,
    explain_hints,
    explain_sweeps,
    print_recap,
    show_sweep_config,
)

LESSON_DIR = Path(__file__).resolve().parent
SWEEP_CONFIG = LESSON_DIR / "sweep-config.yaml"
TASKS_DIR = LESSON_DIR / "tasks"


def check_prerequisites() -> bool:
    """Verify Docker and Harbor are available."""
    print("=" * 60)
    print("Step 0: Checking Prerequisites")
    print("=" * 60)

    # Check Docker
    if shutil.which("docker") is None:
        print("ERROR: Docker is not installed. Please install Docker first.")
        return False
    result = subprocess.run(
        ["docker", "info"], capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        print("ERROR: Docker is not running. Please start Docker first.")
        return False
    print("  [OK] Docker is installed and running.")

    # Check Harbor
    if shutil.which("harbor") is None:
        print("ERROR: Harbor is not installed.")
        print("  Install with: uv tool install harbor")
        return False
    print("  [OK] Harbor is installed.")
    print()
    return True


def run_sweep() -> list[Path]:
    """Run a sweep using the oracle agent and return job directories."""
    print("=" * 60)
    print("Step 4: Running a Sweep")
    print("=" * 60)
    print()

    cmd = [
        "harbor", "sweeps", "run",
        "-c", str(SWEEP_CONFIG),
        "--max-sweeps", "2",
        "--trials-per-task", "1",
    ]

    print(f"Command: {' '.join(cmd)}")
    print()
    print("Running sweep (this may take a minute or two)...")
    print("-" * 40)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(LESSON_DIR),
        timeout=600,
    )

    if result.stdout:
        for line in result.stdout.strip().splitlines():
            print(f"  {line}")
    if result.stderr:
        for line in result.stderr.strip().splitlines():
            print(f"  [stderr] {line}")
    print("-" * 40)

    if result.returncode != 0:
        print(f"WARNING: Sweep exited with code {result.returncode}")
    else:
        print("Sweep completed successfully.")
    print()

    # Collect job directories
    jobs_dir = LESSON_DIR / "jobs"
    job_dirs: list[Path] = []
    if jobs_dir.exists():
        job_dirs = sorted(
            [d for d in jobs_dir.iterdir() if d.is_dir()],
            key=lambda p: p.stat().st_mtime,
        )
    return job_dirs


def analyze_results(job_dirs: list[Path]) -> None:
    """Parse and display sweep results from the jobs/ directory."""
    print("=" * 60)
    print("Step 5: Understanding Sweep Results")
    print("=" * 60)
    print()

    if not job_dirs:
        print("No job directories found in jobs/. Skipping analysis.")
        print("(This can happen if Docker is not running or the sweep failed.)")
        print()
        return

    print(f"Found {len(job_dirs)} job directory(ies) from the sweep:")
    for jd in job_dirs:
        print(f"  - {jd.name}")
    print()

    for job_idx, job_dir in enumerate(job_dirs, 1):
        print(f"--- Sweep Round {job_idx}: {job_dir.name} ---")
        trial_dirs = sorted(d for d in job_dir.iterdir() if d.is_dir())

        for trial_dir in trial_dirs:
            result_path = trial_dir / "result.json"
            if not result_path.exists():
                continue
            try:
                data = json.loads(result_path.read_text())
                if not isinstance(data, dict):
                    continue
                task_name = data.get("task_name", trial_dir.name)
                vr = data.get("verifier_result") or {}
                rewards = vr.get("rewards") or {}
                reward = rewards.get("reward", "N/A") if isinstance(rewards, dict) else "N/A"
                passed = isinstance(reward, (int, float)) and reward > 0
                status = "PASS" if passed else "FAIL"
                print(f"  Task: {task_name:<35} Reward: {reward}  [{status}]")
            except (json.JSONDecodeError, OSError) as e:
                print(f"  Error reading {result_path}: {e}")
        print()

    print("In a real sweep scenario:")
    print("  - Round 1 runs all 3 tasks. The oracle agent should pass all.")
    print("  - Tasks with reward > 0 are dropped from future rounds.")
    print("  - If all pass in Round 1, Round 2 is skipped entirely.")
    print("  - Failed tasks would carry over to subsequent rounds.")
    print()


def main() -> None:
    """Run the Configuration Sweeps lesson."""
    print()
    print("=" * 60)
    print("  Harbor Tutorial")
    print("  Module 11, Lesson 3: Configuration Sweeps")
    print("=" * 60)
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_sweeps()
    show_sweep_config(SWEEP_CONFIG, TASKS_DIR)
    explain_cli_flags()

    job_dirs = run_sweep()
    analyze_results(job_dirs)

    explain_hints()
    print_recap()


if __name__ == "__main__":
    main()
