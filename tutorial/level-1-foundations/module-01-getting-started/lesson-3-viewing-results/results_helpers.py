"""
Helper functions for inspecting Harbor job results.
"""

import json
from pathlib import Path


def print_tree(directory: Path, prefix: str = "", max_depth: int = 4, _depth: int = 0) -> None:
    """Print a directory tree up to max_depth levels."""
    if _depth >= max_depth:
        return

    try:
        entries = sorted(directory.iterdir())
    except PermissionError:
        return

    dirs = [e for e in entries if e.is_dir()]
    files = [e for e in entries if e.is_file()]

    for f in files:
        print(f"{prefix}├── {f.name}")

    for i, d in enumerate(dirs):
        is_last = i == len(dirs) - 1
        connector = "└── " if is_last and not files else "├── "
        print(f"{prefix}{connector}{d.name}/")
        child_prefix = prefix + ("    " if is_last else "│   ")
        print_tree(d, child_prefix, max_depth, _depth + 1)


def find_latest_trial(jobs_dir: Path) -> Path | None:
    """Find the most recently modified trial directory."""
    trial_dirs: list[Path] = []
    for job_dir in jobs_dir.iterdir():
        if job_dir.is_dir():
            for trial_dir in job_dir.iterdir():
                if trial_dir.is_dir():
                    trial_dirs.append(trial_dir)

    if not trial_dirs:
        return None
    return max(trial_dirs, key=lambda p: p.stat().st_mtime)


def find_file_recursive(directory: Path, filename: str) -> Path | None:
    """Recursively search for a file by name."""
    for path in directory.rglob(filename):
        return path
    return None


def print_config_highlights(config: dict) -> None:
    """Print the most important fields from config.json."""
    agent_name = config.get("agent", {}).get("name", "N/A")
    task_name = config.get("task", {}).get("name", "N/A")
    env_type = config.get("environment", {}).get("type", "N/A")

    print(f"  Agent:       {agent_name}")
    print(f"  Task:        {task_name}")
    print(f"  Environment: {env_type}")

    other_keys = [k for k in config if k not in ("agent", "task", "environment")]
    if other_keys:
        print(f"  Other fields: {', '.join(other_keys)}")


def print_result_highlights(result: dict) -> None:
    """Print the most important fields from result.json."""
    reward = result.get("reward", "N/A")
    status = result.get("status", "N/A")
    duration = result.get("duration_sec", result.get("duration", "N/A"))

    print(f"  Reward:   {reward}")
    print(f"  Status:   {status}")
    if duration != "N/A":
        print(f"  Duration: {duration}s")

    for key in ("error", "agent_error", "verifier_error"):
        if result.get(key):
            print(f"  {key}: {result[key]}")


def inspect_trial_results(jobs_dir: Path) -> None:
    """Read and display config.json and result.json from the trial."""
    print("=" * 60)
    print("Step 4: Inspecting Trial Results")
    print("=" * 60)
    print()

    trial_dir = find_latest_trial(jobs_dir)
    if trial_dir is None:
        print("  No trial results found in jobs/ directory.")
        return

    print(f"Trial directory: {trial_dir}")
    print()

    # Read config.json
    config_file = trial_dir / "config.json"
    if config_file.exists():
        print("-" * 40)
        print("config.json — Trial Configuration")
        print("-" * 40)
        config = json.loads(config_file.read_text())
        print_config_highlights(config)
        print()

    # Read result.json
    result_file = trial_dir / "result.json"
    if result_file.exists():
        print("-" * 40)
        print("result.json — Trial Outcome")
        print("-" * 40)
        result_data = json.loads(result_file.read_text())
        print_result_highlights(result_data)
        print()

    # Read reward.txt
    reward_file = find_file_recursive(trial_dir, "reward.txt")
    if reward_file is not None:
        print("-" * 40)
        print("reward.txt — The Final Score")
        print("-" * 40)
        reward = reward_file.read_text().strip()
        print(f"  Reward: {reward}")
        if reward == "1":
            print("  Interpretation: The agent PASSED (full marks)")
        elif reward == "0":
            print("  Interpretation: The agent FAILED")
        else:
            try:
                print(f"  Interpretation: Partial credit ({float(reward) * 100:.0f}%)")
            except ValueError:
                print("  Interpretation: Could not parse reward value")
        print()
