"""Helpers for parsing and displaying SWE-bench results."""

import json
from pathlib import Path


def find_latest_job(jobs_dir: Path) -> Path | None:
    """Find the most recently modified job directory."""
    if not jobs_dir.exists():
        return None
    job_dirs = sorted(
        [d for d in jobs_dir.iterdir() if d.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return job_dirs[0] if job_dirs else None


def load_trial_results(job_dir: Path) -> list[dict]:
    """Load all result.json files from a job directory."""
    results: list[dict] = []
    for result_file in sorted(job_dir.rglob("result.json")):
        try:
            data = json.loads(result_file.read_text())
            results.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return results


def print_results_table(results: list[dict]) -> None:
    """Print a formatted results table with per-instance and aggregate stats."""
    print(f"  {'Instance':<45} {'Reward':>7} {'Duration':>10}")
    print(f"  {'─' * 45} {'─' * 7} {'─' * 10}")

    total_reward = 0.0
    total_duration = 0.0
    passed = 0

    for r in results:
        task_name = r.get("task", {}).get("name", "unknown")
        short_name = task_name.split("/")[-1] if "/" in task_name else task_name
        if len(short_name) > 44:
            short_name = short_name[:41] + "..."

        reward = r.get("reward", 0.0)
        duration = r.get("duration_sec", 0.0)
        total_reward += reward
        total_duration += duration
        if reward >= 1.0:
            passed += 1

        status = "PASS" if reward >= 1.0 else "FAIL"
        print(f"  {short_name:<45} {status:>7} {duration:>8.1f}s")

    n = len(results)
    avg = total_reward / n if n > 0 else 0.0
    print(f"  {'─' * 45} {'─' * 7} {'─' * 10}")
    print(f"  {'TOTAL':<45} {passed}/{n:>4} {total_duration:>8.1f}s")
    print()
    print(f"  Pass rate:      {passed}/{n} ({avg * 100:.1f}%)")
    print(f"  Mean reward:    {avg:.3f}")
    print(f"  Total duration: {total_duration:.0f}s ({total_duration / 60:.1f} min)")
