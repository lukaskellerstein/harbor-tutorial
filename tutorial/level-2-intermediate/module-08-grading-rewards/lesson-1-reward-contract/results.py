"""Helpers for running a Harbor task and reading back what the verifier scored.

Two files matter after a run:

  jobs/<timestamp>/result.json                 -- job level: aggregated metrics
  jobs/<timestamp>/<trial>/result.json         -- trial level: raw rewards dict
"""

import json
import subprocess
from pathlib import Path


def run_task(lesson_dir: Path, task_name: str, agent: str = "oracle") -> bool:
    """Run one task with `harbor run` and stream its output. Returns success.

    `-y` is required here: a task with a [verifier.env] section makes Harbor
    stop and ask permission to read those variables off your host. That prompt
    has no stdin to read from when the run is driven from a script, so without
    `-y` the run aborts.
    """
    task_path = lesson_dir / "tasks" / task_name
    cmd = ["harbor", "run", "-p", str(task_path), "-a", agent, "-y"]

    print(f"  $ harbor run -p tasks/{task_name} -a {agent} -y")
    print()

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(lesson_dir)
    )
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


def trial_rewards(job_dir: Path) -> dict[str, float]:
    """Read the rewards dict from the single trial inside a job directory.

    Harbor stores it at verifier_result.rewards -- ALWAYS a dict, even when the
    task wrote a bare float to reward.txt (that becomes {"reward": <float>}).
    """
    for trial_dir in sorted(job_dir.iterdir()):
        result_file = trial_dir / "result.json"
        if not trial_dir.is_dir() or not result_file.exists():
            continue
        result = json.loads(result_file.read_text())
        verifier_result = result.get("verifier_result") or {}
        return verifier_result.get("rewards") or {}
    return {}


def job_metrics(job_dir: Path) -> list[dict]:
    """Read the aggregated metrics Harbor computed for the job.

    With one distinct reward key across trials you get a single metric named
    after the metric type ({"mean": 0.67}). With several keys you get one entry
    per key ({"sections": 1.0, "title": 1.0, ...}).
    """
    result_file = job_dir / "result.json"
    if not result_file.exists():
        return []
    result = json.loads(result_file.read_text())
    evals = (result.get("stats") or {}).get("evals") or {}
    metrics: list[dict] = []
    for eval_stats in evals.values():
        metrics.extend(eval_stats.get("metrics") or [])
    return metrics


def show_rewards(label: str, rewards: dict[str, float]) -> None:
    """Print a rewards dict as an aligned table."""
    print(f"  {label}")
    if not rewards:
        print("    (no rewards recorded -- the verifier probably errored)")
        print()
        return
    width = max(len(k) for k in rewards)
    for key, value in rewards.items():
        print(f"    {key:<{width}}  {float(value):>5.2f}")
    print()


def show_verifier_files(job_dir: Path) -> None:
    """List which reward files the verifier actually produced."""
    for trial_dir in sorted(job_dir.iterdir()):
        verifier_dir = trial_dir / "verifier"
        if not trial_dir.is_dir() or not verifier_dir.exists():
            continue
        for name in ("reward.txt", "reward.json"):
            path = verifier_dir / name
            if path.exists():
                content = path.read_text().strip().replace("\n", " ")
                print(f"    {name:<12} {content}")
            else:
                print(f"    {name:<12} (not written)")
        return
