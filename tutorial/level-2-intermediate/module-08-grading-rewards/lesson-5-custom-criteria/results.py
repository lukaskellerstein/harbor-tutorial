"""Helpers for running tasks, reading dimensions, and comparing verifiers."""

import json
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_GATEWAY = "http://localhost:4000"


def gateway_reachable(base_url: str = DEFAULT_GATEWAY) -> bool:
    """True if the LiteLLM gateway answers its unauthenticated liveliness probe."""
    try:
        with urllib.request.urlopen(f"{base_url}/health/liveliness", timeout=5) as resp:
            return resp.status == 200
    except (urllib.error.URLError, OSError):
        return False


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
    """Read reward-details.json -- one entry per reward dimension."""
    trial_dir = _first_trial_dir(job_dir)
    if trial_dir is None:
        return None
    details_path = trial_dir / "verifier" / "reward-details.json"
    if not details_path.exists():
        return None
    return json.loads(details_path.read_text())


def show_dimensions(rewards: dict[str, float], aggregated: set[str]) -> None:
    """Print reward keys, separating per-dimension scores from aggregated ones."""
    if not rewards:
        print("    (no rewards recorded -- the verifier errored)")
        print()
        return

    width = max(len(k) for k in rewards)
    print("    per-dimension (one per tests/ subdirectory):")
    for key, value in rewards.items():
        if key not in aggregated:
            print(f"      {key:<{width}}  {float(value):>5.2f}")
    print()
    print("    aggregated (added by tests/reward.toml):")
    for key in aggregated:
        if key in rewards:
            print(f"      {key:<{width}}  {float(rewards[key]):>5.2f}")
    print()


def show_criteria_by_dimension(details: dict | None) -> None:
    """Print every criterion, grouped under the dimension it belongs to."""
    if not details:
        print("    (no reward-details.json found)")
        print()
        return

    for dimension, entry in details.items():
        for reward in entry if isinstance(entry, list) else [entry]:
            kind = reward.get("kind", "?")
            score = float(reward.get("score", 0.0))
            print(f"    {dimension}  ({kind})  ->  {score:.2f}")
            for criterion in reward.get("criteria", []):
                name = str(criterion.get("name", "?"))[:48]
                value = float(criterion.get("value", 0.0))
                weight = float(criterion.get("weight", 1.0))
                print(f"      {name:<48} {value:>5.2f}  x{weight:g}")
            print()
