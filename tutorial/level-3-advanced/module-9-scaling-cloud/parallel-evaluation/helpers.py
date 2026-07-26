"""
Parallel Evaluation — Job config generation and evaluation runner helpers.
"""

import subprocess
import time
from pathlib import Path
from typing import Any

import yaml


def generate_configs(configs_dir: Path, tasks_dir: Path) -> None:
    """Generate serial and parallel job config files."""
    serial_config: dict[str, Any] = {
        "datasets": [{"path": str(tasks_dir)}],
        "agents": [{"name": "oracle"}],
        "environment": {"type": "docker", "delete": True},
        "n_concurrent_trials": 1,
        "quiet": False,
    }

    parallel_config: dict[str, Any] = {
        "datasets": [{"path": str(tasks_dir)}],
        "agents": [{"name": "oracle"}],
        "environment": {"type": "docker", "delete": True},
        "n_concurrent_trials": 4,
        "quiet": False,
    }

    for name, config in [("serial.yaml", serial_config), ("parallel.yaml", parallel_config)]:
        filepath = configs_dir / name
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        print(f"\n  Generated: configs/{name}")
        print(f"  Concurrency: {config['n_concurrent_trials']}")
        for line in yaml.dump(config, default_flow_style=False, sort_keys=False).splitlines():
            print(f"    {line}")
    print()


def run_evaluation(config_path: Path, label: str, cwd: Path) -> float:
    """Run an evaluation and return wall-clock time in seconds."""
    print(f"\n  Running: harbor run -c {config_path}")
    print(f"  Mode: {label}")
    print("  " + "-" * 50)

    start = time.time()
    result = subprocess.run(
        ["harbor", "run", "-c", str(config_path)],
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )
    elapsed = time.time() - start

    if result.stdout:
        for line in result.stdout.strip().splitlines()[-10:]:
            print(f"  {line}")
    if result.returncode != 0 and result.stderr:
        for line in result.stderr.strip().splitlines()[-5:]:
            print(f"  [stderr] {line}")

    print("  " + "-" * 50)
    print(f"  Wall-clock time: {elapsed:.1f} seconds")
    return elapsed
