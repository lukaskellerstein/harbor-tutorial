"""
Helper module: result parsing and display for the hf-datasets lesson.
"""

import json
from pathlib import Path


def _latest_job_dir(lesson_dir: Path) -> Path | None:
    jobs_dir = lesson_dir / "jobs"
    if not jobs_dir.exists():
        return None
    job_dirs = sorted((d for d in jobs_dir.iterdir() if d.is_dir()), reverse=True)
    return job_dirs[0] if job_dirs else None


def display_results(lesson_dir: Path) -> None:
    """Display per-task results from the jobs directory."""
    print("=" * 60)
    print("Step 6: Inspecting Results")
    print("=" * 60)
    print()

    latest_job = _latest_job_dir(lesson_dir)
    if latest_job is None:
        print("No job results found. The evaluation may not have run.")
        print()
        return

    print(f"Latest job: {latest_job.name}")
    print()

    rewards: dict[str, float] = {}
    task_id = None
    source = None

    for trial_dir in sorted(latest_job.iterdir()):
        result_file = trial_dir / "result.json"
        if not trial_dir.is_dir() or not result_file.exists():
            continue

        data = json.loads(result_file.read_text())
        task_name = data.get("task_name") or trial_dir.name
        reward = data.get("verifier_result", {}).get("rewards", {}).get("reward")
        if reward is not None:
            rewards[task_name] = reward
        task_id = data.get("task_id") or task_id
        source = data.get("source") or source

    if task_id:
        print("Where the task files actually came from (from result.json):")
        print(f"  git_url:       {task_id.get('git_url')}")
        print(f"  git_commit_id: {task_id.get('git_commit_id')}")
        print(f"  path:          {task_id.get('path')}")
        print()
        print("The branch reference 'main' was resolved to that immutable SHA")
        print("before anything was downloaded. Pass the SHA with @<sha> to")
        print("reproduce this exact run later, even if the branch moves on.")
        print()

    if source:
        print(f"Dataset name Harbor assigned:\n  {source}")
        print()

    if not rewards:
        print("No per-trial rewards found.")
        print()
        return

    print(f"{'Task':<40} {'Reward':>8}")
    print("-" * 49)
    for task_name, reward in rewards.items():
        print(f"{task_name:<40} {reward:>8.2f}")
    print("-" * 49)

    mean = sum(rewards.values()) / len(rewards)
    print(f"{'Mean':<40} {mean:>8.2f}")
    print()

    if mean == 1.0:
        print("Reward 1.0 -- the reference solution ran against real task files")
        print("fetched from Hugging Face, including the LFS-backed 11 MB SQLite")
        print("database. The whole pipeline resolved correctly.")
    elif mean == 0.0:
        print("Reward 0.0 across the board is the classic Git LFS symptom --")
        print("see Step 7 below.")
    print()
