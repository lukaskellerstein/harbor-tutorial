"""Helper functions for the utility-agents lesson."""

import json
import subprocess
from pathlib import Path


def check_prerequisites() -> bool:
    """Verify that Docker and Harbor are available."""
    print("=" * 60)
    print("Checking prerequisites")
    print("=" * 60)

    result = subprocess.run(
        ["docker", "info"], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        print("ERROR: Docker is not running. Please start Docker and try again.")
        return False
    print("[OK] Docker is running")

    result = subprocess.run(
        ["harbor", "--help"], capture_output=True, text=True, check=False
    )
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

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    return result


def get_latest_trial_result(trials_dir: str) -> dict | None:
    """Read result.json from the most recent trial."""
    trials_path = Path(trials_dir)
    if not trials_path.exists():
        return None

    trial_dirs = sorted(trials_path.iterdir())
    if not trial_dirs:
        return None

    result_path = trial_dirs[-1] / "result.json"
    if not result_path.exists():
        return None

    return json.loads(result_path.read_text())


def get_reward(result: dict | None) -> str:
    """Extract the reward value from a trial result dict."""
    if not result:
        return "N/A"
    rewards = result.get("verifier_result", {}).get("rewards", [])
    return str(rewards[0]) if rewards else "N/A"


def get_agent_name(result: dict | None) -> str:
    """Extract the agent name from a trial result dict."""
    if not result:
        return "N/A"
    return result.get("agent_info", {}).get("name", "N/A")


def get_exception(result: dict | None) -> str:
    """Extract exception info from a trial result dict."""
    if not result:
        return "N/A"
    exc = result.get("exception_info")
    return exc.get("exception_type", "Error") if exc else "None"
