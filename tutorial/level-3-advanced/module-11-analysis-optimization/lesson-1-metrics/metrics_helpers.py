"""
Helper module: result parsing, metric computation, and display for the
metrics lesson.
"""

import json
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TrialInfo:
    """Parsed information from a single trial result."""

    task_name: str
    reward: float
    difficulty: str
    agent_name: str


@dataclass
class AggregateMetrics:
    """Aggregate metrics computed over a set of trials."""

    count: int = 0
    mean_reward: float = 0.0
    max_reward: float = 0.0
    min_reward: float = 0.0
    sum_reward: float = 0.0
    pass_rate: float = 0.0
    pass_at_1: float = 0.0


def parse_trial_results(
    jobs_dir: Path, tasks_dir: Path
) -> list[TrialInfo]:
    """Parse result.json files from the latest job and enrich with task metadata.

    Args:
        jobs_dir: Path to the jobs/ directory.
        tasks_dir: Path to the tasks/ directory (for reading task.toml metadata).

    Returns:
        List of TrialInfo objects, one per completed trial.
    """
    if not jobs_dir.exists():
        return []

    # Find the most recent job directory
    job_dirs = sorted(
        [d for d in jobs_dir.iterdir() if d.is_dir()], reverse=True
    )
    if not job_dirs:
        return []

    latest_job = job_dirs[0]
    print(f"  Latest job directory: {latest_job.name}")

    # Build a lookup from task name to difficulty using task.toml files
    difficulty_map = _build_difficulty_map(tasks_dir)

    trials: list[TrialInfo] = []
    for trial_dir in sorted(latest_job.iterdir()):
        if not trial_dir.is_dir():
            continue

        result_file = trial_dir / "result.json"
        if not result_file.exists():
            continue

        try:
            result = json.loads(result_file.read_text())
        except (json.JSONDecodeError, OSError):
            continue

        # Extract task name
        task_name = result.get("task_name", trial_dir.name)

        # Extract reward from verifier_result.rewards dict
        reward = _extract_reward(result)

        # Extract agent name
        agent_info = result.get("agent_info", {})
        agent_name = agent_info.get("name", "unknown")

        # Look up difficulty from task.toml metadata
        difficulty = difficulty_map.get(task_name, "unknown")

        trials.append(
            TrialInfo(
                task_name=task_name,
                reward=reward,
                difficulty=difficulty,
                agent_name=agent_name,
            )
        )

    return trials


def _extract_reward(result: dict) -> float:
    """Extract the reward value from a result.json structure.

    The verifier_result.rewards field is a dict like {"reward": 1.0}.
    """
    verifier_result = result.get("verifier_result")
    if verifier_result is None:
        return 0.0

    rewards = verifier_result.get("rewards")
    if rewards is None:
        return 0.0

    if isinstance(rewards, dict):
        return float(rewards.get("reward", 0.0))

    return 0.0


def _build_difficulty_map(tasks_dir: Path) -> dict[str, str]:
    """Read task.toml files to build a mapping from task name to difficulty."""
    difficulty_map: dict[str, str] = {}

    if not tasks_dir.exists():
        return difficulty_map

    for task_dir in tasks_dir.iterdir():
        if not task_dir.is_dir():
            continue
        toml_path = task_dir / "task.toml"
        if not toml_path.exists():
            continue

        try:
            with open(toml_path, "rb") as f:
                config = tomllib.load(f)
            task_name = config.get("task", {}).get("name", "")
            difficulty = config.get("metadata", {}).get("difficulty", "unknown")
            if task_name:
                difficulty_map[task_name] = difficulty
        except (OSError, tomllib.TOMLDecodeError):
            continue

    return difficulty_map


def compute_metrics(trials: list[TrialInfo]) -> AggregateMetrics:
    """Compute aggregate metrics from a list of trial results."""
    if not trials:
        return AggregateMetrics()

    rewards = [t.reward for t in trials]
    count = len(rewards)
    total = sum(rewards)
    passed = sum(1 for r in rewards if r > 0)
    perfect = sum(1 for r in rewards if r == 1.0)

    return AggregateMetrics(
        count=count,
        mean_reward=total / count,
        max_reward=max(rewards),
        min_reward=min(rewards),
        sum_reward=total,
        pass_rate=passed / count,
        pass_at_1=perfect / count,
    )


def display_per_task_results(trials: list[TrialInfo]) -> None:
    """Print a formatted table of per-task results."""
    print(f"  {'Task':<40} {'Difficulty':<12} {'Reward':>8}  Status")
    print(f"  {'-' * 40} {'-' * 12} {'-' * 8}  {'-' * 7}")
    for t in trials:
        if t.reward == 1.0:
            status = "PASS"
        elif t.reward > 0:
            status = "PARTIAL"
        else:
            status = "FAIL"
        print(f"  {t.task_name:<40} {t.difficulty:<12} {t.reward:>8.2f}  [{status}]")
    print()


def display_aggregate_metrics(metrics: AggregateMetrics) -> None:
    """Print aggregate metrics in a clear format."""
    print(f"  Total trials:    {metrics.count}")
    print(f"  Mean reward:     {metrics.mean_reward:.4f}")
    print(f"  Max reward:      {metrics.max_reward:.2f}")
    print(f"  Min reward:      {metrics.min_reward:.2f}")
    print(f"  Sum of rewards:  {metrics.sum_reward:.2f}")
    print(f"  Pass rate:       {metrics.pass_rate:.1%}  (reward > 0)")
    print(f"  Pass@1:          {metrics.pass_at_1:.1%}  (reward == 1.0)")
    print()


def display_grouped_by_difficulty(trials: list[TrialInfo]) -> None:
    """Group trials by difficulty and display per-group metrics."""
    groups: dict[str, list[TrialInfo]] = {}
    for t in trials:
        groups.setdefault(t.difficulty, []).append(t)

    # Sort by difficulty in a logical order
    order = {"easy": 0, "medium": 1, "hard": 2}
    sorted_groups = sorted(groups.items(), key=lambda x: order.get(x[0], 99))

    print(f"  {'Difficulty':<12} {'Count':>6} {'Mean':>8} {'Pass Rate':>10} {'Pass@1':>8}")
    print(f"  {'-' * 12} {'-' * 6} {'-' * 8} {'-' * 10} {'-' * 8}")

    for difficulty, group_trials in sorted_groups:
        m = compute_metrics(group_trials)
        print(
            f"  {difficulty:<12} {m.count:>6} {m.mean_reward:>8.4f} "
            f"{m.pass_rate:>9.1%} {m.pass_at_1:>7.1%}"
        )
    print()
