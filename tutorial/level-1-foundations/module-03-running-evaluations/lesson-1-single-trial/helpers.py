"""Helper functions for the single-trial lesson."""

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


def find_latest_trial(trials_dir: str = "trials") -> Path | None:
    """Find the most recent trial directory."""
    trials_path = Path(trials_dir)
    if not trials_path.exists():
        return None

    trial_dirs = sorted(trials_path.iterdir())
    return trial_dirs[-1] if trial_dirs else None


def read_trial_result(trial_dir: Path) -> dict | None:
    """Read result.json from a trial directory."""
    result_path = trial_dir / "result.json"
    if not result_path.exists():
        return None
    return json.loads(result_path.read_text())
