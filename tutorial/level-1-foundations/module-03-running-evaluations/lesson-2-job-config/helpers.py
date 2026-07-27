"""Helper functions for the job-config lesson."""

import json
import subprocess
from pathlib import Path


def check_prerequisites() -> bool:
    """Verify that Docker and Harbor are available."""
    print("=" * 60)
    print("Checking prerequisites")
    print("=" * 60)

    result = subprocess.run(["docker", "info"], capture_output=True, text=True)
    if result.returncode != 0:
        print("ERROR: Docker is not running. Please start Docker and try again.")
        return False
    print("[OK] Docker is running")

    result = subprocess.run(["harbor", "--help"], capture_output=True, text=True)
    if result.returncode != 0:
        print("ERROR: Harbor is not installed. Run: uv tool install harbor")
        return False
    print("[OK] Harbor is installed")
    print()
    return True


def run_harbor_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a harbor CLI command and print its output."""
    print(f"Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    return result


def find_latest_dir(parent: str) -> Path | None:
    """Find the most recent subdirectory."""
    parent_path = Path(parent)
    if not parent_path.exists():
        return None

    dirs = sorted(parent_path.iterdir())
    return dirs[-1] if dirs else None


def print_trial_summary(trial_dir: Path) -> None:
    """Print a one-line summary of a trial."""
    result_path = trial_dir / "result.json"
    if not result_path.exists():
        print(f"  {trial_dir.name}: (no result.json)")
        return

    data = json.loads(result_path.read_text())
    task_name = data.get("task_name", "unknown")
    rewards = data.get("verifier_result", {}).get("rewards", [])
    reward_str = ", ".join(str(r) for r in rewards) if rewards else "N/A"
    exc = data.get("exception_info")

    status = "PASS" if rewards and all(r == 1.0 for r in rewards) else "FAIL"
    if exc:
        status = "ERROR"

    print(f"  {trial_dir.name}")
    print(f"    Task:    {task_name}")
    print(f"    Reward:  {reward_str}")
    print(f"    Status:  {status}")
    if exc:
        print(f"    Error:   {exc.get('exception_type', 'N/A')}")
    print()
