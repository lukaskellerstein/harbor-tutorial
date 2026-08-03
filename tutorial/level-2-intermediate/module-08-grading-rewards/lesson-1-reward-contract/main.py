"""
Module 8, Lesson 1: Rewards & the Verifier Contract

Three tasks, three grading styles:
  1. reward-txt         one float, always keyed "reward"
  2. reward-json        named dimensions that keep their identity
  3. reward-precedence  both files, conflicting values -- who wins?
"""

import shutil
import subprocess
import sys
from pathlib import Path

from results import (
    job_metrics,
    latest_job_dir,
    run_task,
    show_rewards,
    show_verifier_files,
    trial_rewards,
)

LESSON_DIR = Path(__file__).parent


def check_prerequisites() -> bool:
    """Verify Docker and Harbor are available."""
    print("=" * 60)
    print("Checking Prerequisites")
    print("=" * 60)

    docker_ok = shutil.which("docker") is not None
    harbor_ok = shutil.which("harbor") is not None
    docker_running = subprocess.run(["docker", "info"], capture_output=True, text=True, check=False).returncode == 0

    print(f"  Docker CLI:     {'[OK]' if docker_ok else '[MISSING]'}")
    print(f"  Docker running: {'[OK]' if docker_running else '[NOT RUNNING]'}")
    print(f"  Harbor CLI:     {'[OK]' if harbor_ok else '[MISSING]'}")
    print()

    if not (docker_ok and docker_running and harbor_ok):
        print("  Prerequisites not met. Fix the issues above.")
        return False
    return True


def explain_contract() -> None:
    """Step 1: the two reward file formats."""
    print("=" * 60)
    print("Step 1: The Verifier Contract")
    print("=" * 60)
    print()
    print("  A verifier communicates with Harbor through ONE of two files:")
    print()
    print("    /logs/verifier/reward.txt    a single float, e.g.  0.67")
    print("    /logs/verifier/reward.json   a flat JSON object, e.g.")
    print('                                 {"accuracy": 0.9, "style": 0.5}')
    print()
    print("  Harbor normalizes both into a dict. reward.txt becomes")
    print('  {"reward": 0.67} -- the name is not yours to choose.')
    print()
    print("  reward.json lets you name each dimension, and any number of them.")
    print()


def step_reward_txt() -> None:
    """Step 2: single-dimension grading."""
    print("=" * 60)
    print("Step 2: One Number (reward.txt)")
    print("=" * 60)
    print()
    print("  The verifier checks three sections and averages them into one float.")
    print("  Three independent facts collapse into a single number.")
    print()

    if not run_task(LESSON_DIR, "reward-txt"):
        print("  Trial failed. Skipping analysis.")
        return

    job_dir = latest_job_dir(LESSON_DIR)
    if job_dir is None:
        return

    show_rewards("Rewards recorded on the trial:", trial_rewards(job_dir))
    print(f"  Job metrics: {job_metrics(job_dir)}")
    print("  One reward key across the job -> one metric, named after the")
    print("  metric type (mean), not after anything the task chose.")
    print()


def step_reward_json() -> None:
    """Step 3: multi-dimension grading."""
    print("=" * 60)
    print("Step 3: Named Dimensions (reward.json)")
    print("=" * 60)
    print()
    print("  Same three checks -- but each keeps its own name and score.")
    print()

    if not run_task(LESSON_DIR, "reward-json"):
        print("  Trial failed. Skipping analysis.")
        return

    job_dir = latest_job_dir(LESSON_DIR)
    if job_dir is None:
        return

    show_rewards("Rewards recorded on the trial:", trial_rewards(job_dir))
    print(f"  Job metrics: {job_metrics(job_dir)}")
    print("  Several reward keys -> the metric is computed PER KEY, so you can")
    print("  see which dimension an agent is failing, not just that it failed.")
    print()
    print('  Note: this task writes no "reward" key. Tooling that assumes the')
    print("  one-dimensional convention (min_reward gates, harbor analyze")
    print("  --passing/--failing, harbor check) will not find a score here.")
    print()


def step_precedence() -> None:
    """Step 4: which file wins."""
    print("=" * 60)
    print("Step 4: Precedence -- reward.json Beats reward.txt")
    print("=" * 60)
    print()
    print("  This verifier writes BOTH files, with conflicting values:")
    print("    reward.txt  -> 0.00  (a deliberate lie)")
    print('    reward.json -> the real scores, plus a "reward" roll-up')
    print()

    if not run_task(LESSON_DIR, "reward-precedence"):
        print("  Trial failed. Skipping analysis.")
        return

    job_dir = latest_job_dir(LESSON_DIR)
    if job_dir is None:
        return

    print("  Files the verifier left behind:")
    show_verifier_files(job_dir)
    print()

    rewards = trial_rewards(job_dir)
    show_rewards("Rewards Harbor actually recorded:", rewards)

    if rewards and float(rewards.get("reward", 0)) > 0:
        print("  reward.json won. The 0.00 in reward.txt was never read.")
    else:
        print("  Unexpected: reward.txt appears to have won. Check the trial log.")
    print()
    print("  Source of truth: src/harbor/verifier/verifier.py checks")
    print("  reward.json first and only falls back to reward.txt when the JSON")
    print("  file is absent. The published docs state the opposite -- they are")
    print("  wrong, and Harbor's own unit tests confirm the order above.")
    print()


def show_summary() -> None:
    """Print the lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print('  reward.txt   one float -> always {"reward": <float>}')
    print("  reward.json  {name: number} -> any number of named dimensions")
    print("  Both present -> reward.json wins, reward.txt is ignored")
    print()
    print("  Rules of thumb:")
    print("    - Reach for reward.json the moment you have >1 thing to measure.")
    print('    - Always include a "reward" roll-up alongside your dimensions,')
    print("      or the one-dimensional tooling has nothing to read.")
    print("    - Never write both files -- one of them is dead code.")
    print()
    print("  Next lesson: lesson-2-llm-judge (grading open-ended output)")


def main() -> None:
    """Run the reward-contract lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 2, Module 8          #")
    print("#          Lesson 1: Rewards & the Verifier Contract    #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_contract()
    step_reward_txt()
    step_reward_json()
    step_precedence()
    show_summary()


if __name__ == "__main__":
    main()
