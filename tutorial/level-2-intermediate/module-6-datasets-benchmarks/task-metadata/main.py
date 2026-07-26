"""
Lesson 3: Task Configuration Deep Dive

A comprehensive walkthrough of every section and field in task.toml,
the configuration file that controls how Harbor runs a task.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

from config_reference import (
    explain_advanced_features,
    explain_agent_section,
    explain_artifacts_section,
    explain_environment_env,
    explain_environment_section,
    explain_metadata_section,
    explain_schema_version,
    explain_steps_section,
    explain_task_section,
    explain_verifier_section,
)

LESSON_DIR = Path(__file__).parent
TASK_DIR = LESSON_DIR / "tasks" / "configured-task"


def check_prerequisites() -> bool:
    """Verify Docker and Harbor are available."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
    print("=" * 60)

    docker_ok = shutil.which("docker") is not None
    harbor_ok = shutil.which("harbor") is not None

    if docker_ok:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, text=True
        )
        docker_ok = result.returncode == 0

    print(f"  Docker:  {'[OK]' if docker_ok else '[FAIL] Docker daemon not running'}")
    print(f"  Harbor:  {'[OK]' if harbor_ok else '[FAIL] Install with: uv tool install harbor'}")
    print()

    if not (docker_ok and harbor_ok):
        print("Prerequisites not met. Please fix the issues above.")
        return False
    return True


def show_task_toml() -> None:
    """Display the configured task.toml file."""
    print("=" * 60)
    print("Step 2: The task.toml File")
    print("=" * 60)
    print()
    print("task.toml is the configuration file for every Harbor task.")
    print("It controls identity, metadata, timeouts, environment setup,")
    print("and verification behavior.")
    print()

    toml_path = TASK_DIR / "task.toml"
    if toml_path.exists():
        print(f"Our configured task ({toml_path.name}):")
        print("-" * 60)
        print(toml_path.read_text())
        print("-" * 60)
    print()


def run_configured_task() -> None:
    """Run the configured task to demonstrate settings in action."""
    print("=" * 60)
    print("Step 13: Running the Configured Task")
    print("=" * 60)
    print()
    print(f"Task path: {TASK_DIR}")
    print()
    print("This task uses [environment.env] to pass GREETING_NAME='Harbor'")
    print("into the container. The oracle solution reads this variable")
    print("and creates greeting.txt with 'Hello, Harbor!'.")
    print()
    print(f"Running: harbor run -p {TASK_DIR} -a oracle")
    print("-" * 60)

    result = subprocess.run(
        ["harbor", "run", "-p", str(TASK_DIR), "-a", "oracle"],
        capture_output=True,
        text=True,
        cwd=str(LESSON_DIR),
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    print("-" * 60)
    print()

    # Show the result
    jobs_dir = LESSON_DIR / "jobs"
    if jobs_dir.exists():
        job_dirs = sorted(jobs_dir.iterdir(), reverse=True)
        if job_dirs:
            latest_job = job_dirs[0]
            for trial_dir in sorted(latest_job.iterdir()):
                if not trial_dir.is_dir():
                    continue
                result_file = trial_dir / "result.json"
                if result_file.exists():
                    try:
                        data = json.loads(result_file.read_text())
                        reward = data.get("reward", {})
                        if isinstance(reward, dict):
                            reward_val = reward.get("reward", 0.0)
                        elif isinstance(reward, (int, float)):
                            reward_val = float(reward)
                        else:
                            reward_val = 0.0
                        status = "PASS" if reward_val == 1.0 else "FAIL"
                        print(f"Result: reward = {reward_val:.1f} [{status}]")
                        print()
                        print("The configured timeout, env vars, and resource")
                        print("limits were applied to this trial run.")
                    except (json.JSONDecodeError, KeyError):
                        print("Could not parse result file.")
    print()


def show_summary() -> None:
    """Display lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("task.toml sections at a glance:")
    print()
    print(f"  {'Section':<25} {'Purpose'}")
    print(f"  {'-' * 25} {'-' * 34}")
    print(f"  {'schema_version':<25} {'Format version (currently 1.3)'}")
    print(f"  {'[task]':<25} {'Package identity (name, authors)'}")
    print(f"  {'[metadata]':<25} {'Free-form metadata (difficulty)'}")
    print(f"  {'[agent]':<25} {'Agent timeout, user, network'}")
    print(f"  {'[verifier]':<25} {'Verifier timeout, env, mode'}")
    print(f"  {'[environment]':<25} {'Container: CPU, RAM, network'}")
    print(f"  {'[environment.env]':<25} {'Env vars with ${{VAR}} syntax'}")
    print(f"  {'[solution.env]':<25} {'Env vars for oracle agent'}")
    print(f"  {'[[steps]]':<25} {'Multi-step task definitions'}")
    print(f"  {'[[artifacts]]':<25} {'File collection from container'}")
    print()
    print("Next module: module-7-environments-configuration")
    print("  (Docker environments, environment features, model routing)")


def main() -> None:
    """Run the task-metadata lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 2, Module 6          #")
    print("#          Lesson 3: Task Configuration Deep Dive       #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    show_task_toml()
    explain_schema_version()
    explain_task_section()
    explain_metadata_section()
    explain_agent_section()
    explain_verifier_section()
    explain_environment_section()
    explain_environment_env()
    explain_steps_section()
    explain_artifacts_section()
    explain_advanced_features()
    run_configured_task()
    show_summary()


if __name__ == "__main__":
    main()
