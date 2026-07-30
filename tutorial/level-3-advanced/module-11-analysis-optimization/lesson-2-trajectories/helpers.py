"""Helper functions for the Agent Trajectories lesson."""

import json
import shutil
import subprocess
from pathlib import Path

LESSON_DIR = Path(__file__).parent.resolve()
TASKS_DIR = LESSON_DIR / "tasks"
TRIALS_DIR = LESSON_DIR / "trials"
TRACE_TASK_DIR = TASKS_DIR / "trace-task"


def check_prerequisites() -> bool:
    """Verify Docker and Harbor are available."""
    print("=" * 60)
    print("PREREQUISITES CHECK")
    print("=" * 60)

    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True, text=True, timeout=15,
            check=False,
        )
        if result.returncode != 0:
            print("[ERROR] Docker is not running. Please start Docker first.")
            return False
        print("[OK] Docker is running")
    except FileNotFoundError:
        print("[ERROR] Docker is not installed.")
        return False

    try:
        result = subprocess.run(
            ["harbor", "--help"],
            capture_output=True, text=True, timeout=10,
            check=False,
        )
        if result.returncode != 0:
            print("[ERROR] Harbor CLI returned an error.")
            return False
        print("[OK] Harbor CLI is available")
    except FileNotFoundError:
        print("[ERROR] Harbor is not installed. Run: uv tool install harbor")
        return False

    print()
    return True


def run_trial() -> str | None:
    """Run a trial with the oracle agent and return the trial directory."""
    if TRIALS_DIR.exists():
        shutil.rmtree(TRIALS_DIR)

    cmd = [
        "harbor", "trial", "start",
        "-p", str(TRACE_TASK_DIR),
        "-a", "oracle",
        "--delete",
        "--trials-dir", str(TRIALS_DIR),
    ]
    print(f"Running: {' '.join(cmd)}")
    print()

    result = subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=120,
        cwd=str(LESSON_DIR),
        check=False,
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        print(f"[ERROR] Trial failed with exit code {result.returncode}")
        return None

    if not TRIALS_DIR.exists():
        print("[ERROR] Trials directory was not created.")
        return None

    trial_dirs = [d for d in TRIALS_DIR.iterdir() if d.is_dir()]
    if not trial_dirs:
        print("[ERROR] No trial directory found.")
        return None

    trial_dir = str(trial_dirs[0])
    print(f"Trial output directory: {trial_dir}")
    print()
    return trial_dir


def inspect_trial_output(trial_dir: str) -> None:
    """Walk the trial output directory and explain each file."""
    descriptions: dict[str, str] = {
        "agent": "Agent logs and trajectory (trajectory.json)",
        "verifier": "Test output (test-stdout.txt, test-stderr.txt, reward.txt)",
        "artifacts": "Collected artifacts from the environment",
        "config.json": "Trial configuration for reproducibility",
        "result.json": "Trial results (reward, timing, agent info)",
        "trial.log": "Execution log",
    }

    trial_path = Path(trial_dir)
    for item in sorted(trial_path.rglob("*")):
        rel = item.relative_to(trial_path)
        indent = "  " * (len(rel.parts) - 1)
        marker = "/" if item.is_dir() else ""
        name = item.name + marker
        desc = descriptions.get(item.name, "")
        suffix = f"  <- {desc}" if desc else ""
        print(f"  {indent}{name}{suffix}")

    print()

    result_file = trial_path / "result.json"
    if result_file.exists():
        print("-" * 40)
        print("result.json contents:")
        print("-" * 40)
        data = json.loads(result_file.read_text())
        print(json.dumps(data, indent=2))
        print()
        reward = data.get("verifier_result", {}).get("rewards", {})
        print(f"  Reward: {reward}")
        print()

    verifier_dir = trial_path / "verifier"
    if verifier_dir.exists():
        print("-" * 40)
        print("Verifier output:")
        print("-" * 40)
        for f in sorted(verifier_dir.iterdir()):
            if f.is_file():
                print(f"\n  [{f.name}]")
                content = f.read_text().strip()
                for line in content.splitlines():
                    print(f"    {line}")
        print()

    agent_dir = trial_path / "agent"
    if agent_dir.exists():
        print("-" * 40)
        print("Agent directory contents:")
        print("-" * 40)
        for f in sorted(agent_dir.rglob("*")):
            if f.is_file():
                rel = f.relative_to(agent_dir)
                size = f.stat().st_size
                print(f"  {rel} ({size} bytes)")
        print()


def get_atif_example() -> dict:
    """Return an abbreviated ATIF v1.7 trajectory example."""
    return {
        "schema_version": "ATIF-v1.7",
        "agent": {
            "name": "oracle",
            "version": "0.1.0",
            "model_name": None,
        },
        "steps": [
            {
                "step_id": 1,
                "timestamp": "2026-01-15T10:30:00Z",
                "source": "system",
                "message": "Task instruction provided to agent.",
            },
            {
                "step_id": 2,
                "timestamp": "2026-01-15T10:30:01Z",
                "source": "agent",
                "message": "Creating the required files...",
                "tool_calls": [
                    {
                        "tool_call_id": "call_001",
                        "function_name": "bash",
                        "arguments": {
                            "command": (
                                "cat > /home/user/greeting.py << 'EOF'\n"
                                'print("Hello, Harbor!")\n'
                                "EOF"
                            )
                        },
                    }
                ],
                "observation": {
                    "results": [
                        {"source_call_id": "call_001", "content": "(exit code 0)"}
                    ]
                },
                "metrics": {
                    "prompt_tokens": 150,
                    "completion_tokens": 45,
                    "cost_usd": 0.001,
                },
            },
        ],
        "final_metrics": {
            "total_prompt_tokens": 150,
            "total_completion_tokens": 45,
            "total_cost_usd": 0.001,
        },
    }
