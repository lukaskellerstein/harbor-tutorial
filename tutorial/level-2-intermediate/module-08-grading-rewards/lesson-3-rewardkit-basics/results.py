"""Helpers for running tasks and reading RewardKit's per-criterion breakdown."""

import json
import subprocess
from pathlib import Path


def run_task(lesson_dir: Path, task_name: str, agent: str = "oracle") -> bool:
    """Run one task with `harbor run` and stream its output. Returns success."""
    task_path = lesson_dir / "tasks" / task_name
    cmd = ["harbor", "run", "-p", str(task_path), "-a", agent, "-y"]

    print(f"  $ harbor run -p tasks/{task_name} -a {agent} -y")
    print()

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(lesson_dir))
    for stream in (result.stdout, result.stderr):
        for line in (stream or "").splitlines():
            print(f"    {line}")
    print()
    return result.returncode == 0


def latest_job_dir(lesson_dir: Path) -> Path | None:
    """Return the most recently created job directory, or None."""
    jobs_dir = lesson_dir / "jobs"
    if not jobs_dir.exists():
        return None
    job_dirs = sorted((d for d in jobs_dir.iterdir() if d.is_dir()), reverse=True)
    return job_dirs[0] if job_dirs else None


def _first_trial_dir(job_dir: Path) -> Path | None:
    for trial_dir in sorted(job_dir.iterdir()):
        if trial_dir.is_dir() and (trial_dir / "result.json").exists():
            return trial_dir
    return None


def trial_rewards(job_dir: Path) -> dict[str, float]:
    """Read the rewards dict from the single trial inside a job directory."""
    trial_dir = _first_trial_dir(job_dir)
    if trial_dir is None:
        return {}
    result = json.loads((trial_dir / "result.json").read_text())
    return (result.get("verifier_result") or {}).get("rewards") or {}


def reward_details(job_dir: Path) -> dict | None:
    """Read reward-details.json -- RewardKit's per-criterion breakdown.

    reward.json holds only the final numbers. This file holds every criterion's
    name, value, weight and error, and is what `harbor view jobs` renders under
    Verifier Logs -> Rewards.
    """
    trial_dir = _first_trial_dir(job_dir)
    if trial_dir is None:
        return None
    details_path = trial_dir / "verifier" / "reward-details.json"
    if not details_path.exists():
        return None
    return json.loads(details_path.read_text())


def show_rewards(label: str, rewards: dict[str, float]) -> None:
    """Print a rewards dict as an aligned table."""
    print(f"  {label}")
    if not rewards:
        print("    (no rewards recorded -- the verifier errored)")
        print()
        return
    width = max(len(k) for k in rewards)
    for key, value in rewards.items():
        print(f"    {key:<{width}}  {float(value):>5.2f}")
    print()


def show_criteria(details: dict | None) -> None:
    """Print each criterion's score and weight from reward-details.json.

    Shape (rewardkit/runner.py:_build_details):

        {"<reward name>": {"score": 0.9,
                           "kind": "programmatic" | "llm" | "agent",
                           "criteria": [{"name": ..., "value": ..., ...}]}}

    A reward name maps to a LIST of these when one directory produced several
    rewards (e.g. a .py file and a judge .toml side by side).
    """
    if not details:
        print("    (no reward-details.json found)")
        print()
        return

    for reward_name, entry in details.items():
        entries = entry if isinstance(entry, list) else [entry]
        for reward in entries:
            kind = reward.get("kind", "?")
            score = float(reward.get("score", 0.0))
            print(f"    reward \"{reward_name}\"  ({kind})  ->  {score:.2f}")
            print(f"      {'criterion':<44} {'score':>6} {'weight':>7}")
            print(f"      {'-' * 44} {'-' * 6} {'-' * 7}")
            for criterion in reward.get("criteria", []):
                name = str(criterion.get("name", "?"))[:44]
                value = float(criterion.get("value", 0.0))
                weight = float(criterion.get("weight", 1.0))
                line = f"      {name:<44} {value:>6.2f} {weight:>7.1f}"
                if criterion.get("error"):
                    line += f"  ERROR: {criterion['error']}"
                print(line)
            print()
