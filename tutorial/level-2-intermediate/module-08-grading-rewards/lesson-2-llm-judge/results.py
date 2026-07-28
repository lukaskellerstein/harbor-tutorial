"""Helpers for running a Harbor task and reading back what the judge scored."""

import json
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_GATEWAY = "http://localhost:4000"


def gateway_reachable(base_url: str = DEFAULT_GATEWAY) -> bool:
    """True if the LiteLLM gateway answers its liveliness probe.

    /health/liveliness is unauthenticated; /health would 401 without the key.
    """
    try:
        with urllib.request.urlopen(f"{base_url}/health/liveliness", timeout=5) as resp:
            return resp.status == 200
    except (urllib.error.URLError, OSError):
        return False


def run_task(lesson_dir: Path, task_name: str, agent: str = "oracle") -> bool:
    """Run one task with `harbor run` and stream its output. Returns success.

    `-y` auto-confirms the prompt that [verifier.env] triggers -- Harbor asks
    permission before reading variables off your host, and that prompt has no
    stdin when the run is driven from a script.
    """
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


def trial_rewards(job_dir: Path) -> dict[str, float]:
    """Read the rewards dict from the single trial inside a job directory."""
    for trial_dir in sorted(job_dir.iterdir()):
        result_file = trial_dir / "result.json"
        if not trial_dir.is_dir() or not result_file.exists():
            continue
        result = json.loads(result_file.read_text())
        return (result.get("verifier_result") or {}).get("rewards") or {}
    return {}


def judge_stdout(job_dir: Path) -> str:
    """Read what the judge printed, captured by Harbor at verifier/test-stdout.txt.

    This is where a judge's reasoning ends up -- worth reading whenever a score
    looks wrong.
    """
    for trial_dir in sorted(job_dir.iterdir()):
        stdout_path = trial_dir / "verifier" / "test-stdout.txt"
        if trial_dir.is_dir() and stdout_path.exists():
            return stdout_path.read_text()
    return ""


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
