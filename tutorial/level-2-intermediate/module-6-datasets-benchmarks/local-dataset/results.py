"""
Helper module: result parsing and display for the local-dataset lesson.
"""

import json
from pathlib import Path


def display_results(lesson_dir: Path) -> None:
    """Display per-task results from the jobs directory."""
    print("=" * 60)
    print("Step 5: Inspecting Results")
    print("=" * 60)
    print()

    jobs_dir = lesson_dir / "jobs"
    if not jobs_dir.exists():
        print("No jobs directory found. The evaluation may not have run.")
        return

    # Find the most recent job directory
    job_dirs = sorted(jobs_dir.iterdir(), reverse=True)
    if not job_dirs:
        print("No job results found.")
        return

    latest_job = job_dirs[0]
    print(f"Latest job: {latest_job.name}")
    print()

    # Collect results from trial directories
    rewards: dict[str, float] = {}
    trial_dirs = sorted(latest_job.iterdir())

    for trial_dir in trial_dirs:
        if not trial_dir.is_dir():
            continue
        result_file = trial_dir / "result.json"
        config_file = trial_dir / "config.json"

        task_name = trial_dir.name
        if config_file.exists():
            try:
                config = json.loads(config_file.read_text())
                task_name = config.get("task", {}).get("name", trial_dir.name)
            except (json.JSONDecodeError, KeyError):
                pass

        if result_file.exists():
            try:
                result = json.loads(result_file.read_text())
                reward = result.get("reward", {})
                if isinstance(reward, dict):
                    reward_val = reward.get("reward", 0.0)
                elif isinstance(reward, (int, float)):
                    reward_val = float(reward)
                else:
                    reward_val = 0.0
                rewards[task_name] = reward_val
            except (json.JSONDecodeError, KeyError):
                rewards[task_name] = -1.0

    if rewards:
        print("Per-task results:")
        print(f"  {'Task':<35} {'Reward':>8}")
        print(f"  {'-' * 35} {'-' * 8}")
        for task_name, reward in rewards.items():
            status = "PASS" if reward == 1.0 else "FAIL"
            print(f"  {task_name:<35} {reward:>8.1f}  [{status}]")

        print()
        avg = sum(rewards.values()) / len(rewards) if rewards else 0.0
        print(f"  Aggregate mean reward: {avg:.2f}")
        print(f"  Tasks evaluated:       {len(rewards)}")
        print(f"  Tasks passed:          {sum(1 for r in rewards.values() if r == 1.0)}")
    else:
        print("No results found in trial directories.")
        print("You can also view results with: harbor view jobs")

    print()
