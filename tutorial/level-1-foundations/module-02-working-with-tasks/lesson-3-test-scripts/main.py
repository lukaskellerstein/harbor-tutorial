"""
Lesson 3: Writing Test Scripts

This lesson demonstrates three approaches to writing Harbor test
scripts (verifiers): binary pass/fail, partial-credit, and pytest.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from approaches import APPROACHES

LESSON_DIR = Path(__file__).parent
TASKS_DIR = LESSON_DIR / "tasks"


def check_prerequisites() -> bool:
    """Verify Docker and Harbor are available."""
    print("=" * 60)
    print("Checking Prerequisites")
    print("=" * 60)

    docker_ok = shutil.which("docker") is not None
    harbor_ok = shutil.which("harbor") is not None
    result = subprocess.run(
        ["docker", "info"],
        capture_output=True,
        text=True,
        check=False,
    )
    docker_running = result.returncode == 0

    print(f"  Docker CLI:     {'[OK]' if docker_ok else '[MISSING]'}")
    print(f"  Docker running: {'[OK]' if docker_running else '[NOT RUNNING]'}")
    print(f"  Harbor CLI:     {'[OK]' if harbor_ok else '[MISSING]'}")
    print()

    if not (docker_ok and docker_running and harbor_ok):
        print("  Prerequisites not met. Fix the issues above.")
        return False
    return True


def explain_reward_file() -> None:
    """Explain the reward file mechanism."""
    print("=" * 60)
    print("Step 1: How Test Scripts Work")
    print("=" * 60)
    print()
    print("Every Harbor test script must do ONE thing:")
    print("  Write a number (0 to 1) to /logs/verifier/reward.txt")
    print()
    print("This is the contract between your test and Harbor:")
    print("  - Harbor uploads tests/ into the container")
    print("  - Harbor runs tests/test.sh")
    print("  - Harbor reads /logs/verifier/reward.txt as the reward")
    print()
    print("The reward value determines the trial outcome:")
    print("  0     = complete failure")
    print("  0.5   = partial success")
    print("  1     = full success")
    print()
    print("Let's explore three approaches to writing test scripts.")
    print()


def show_test_script(task_name: str) -> None:
    """Display the test.sh file for a given task."""
    test_path = TASKS_DIR / task_name / "tests" / "test.sh"
    if test_path.exists():
        for line in test_path.read_text().strip().splitlines():
            print(f"    {line}")
    print()


def run_approach(approach: dict[str, str], step_num: int) -> None:
    """Explain and run a single testing approach."""
    print("=" * 60)
    print(f"Step {step_num}: Approach {approach['number']} -- {approach['title']}")
    print("=" * 60)
    print()
    print(f"  {approach['description']}")
    print()
    print(f"  Task: tasks/{approach['task']}/")
    print()
    print("  test.sh contents:")
    print("  " + "-" * 50)
    show_test_script(approach["task"])
    print("  " + "-" * 50)

    task_path = TASKS_DIR / approach["task"]
    print(f"  Running: harbor run -p tasks/{approach['task']} -a oracle")
    print()

    result = subprocess.run(
        ["harbor", "run", "-p", str(task_path), "-a", "oracle"],
        capture_output=True,
        text=True,
        cwd=str(LESSON_DIR),
        check=False,
    )

    if result.stdout:
        for line in result.stdout.splitlines():
            print(f"    {line}")
    if result.stderr:
        for line in result.stderr.splitlines():
            print(f"    {line}")

    print()
    if result.returncode == 0:
        print(f"  Expected reward: {approach['expected_reward']}")
        print("  Trial completed successfully.")
    else:
        print(f"  Trial failed (return code {result.returncode}).")
    print()


def show_summary() -> None:
    """Display the lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("Three approaches to writing test scripts:")
    print()
    print("  1. Binary test      Simple pass/fail (0 or 1).")
    print("  2. Partial credit   Fractional reward (0.33, 0.67, ...).")
    print("  3. Pytest + CTRF    Structured testing. Harbor's default.")
    print()
    print("All three share the same contract:")
    print("  test.sh must write a float (0-1) to /logs/verifier/reward.txt")
    print()
    print("Tips for writing good test scripts:")
    print("  - Always create /logs/verifier/ before writing reward.txt")
    print("  - Exit with 0 even on test failure (let the reward speak)")
    print("  - Print diagnostic output for debugging")
    print("  - Test the actual output, not the method")
    print()
    print("Next lesson: lesson-4-interactive-env (debugging inside containers)")


def main() -> None:
    """Run the test-scripts lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Module 2, Lesson 3         #")
    print("#          Writing Test Scripts                         #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_reward_file()

    for i, approach in enumerate(APPROACHES):
        run_approach(approach, step_num=i + 2)

    show_summary()


if __name__ == "__main__":
    main()
