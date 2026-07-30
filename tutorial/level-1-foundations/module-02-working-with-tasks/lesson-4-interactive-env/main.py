"""
Lesson 4: Debugging with Interactive Environments

This lesson explains how to use Harbor's interactive environment
feature to enter a task container, explore the filesystem, and
debug tasks manually.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from explanations import (
    explain_interactive_mode,
    show_debugging_commands,
    show_debugging_workflow,
    show_interactive_instructions,
    show_task_environment,
)

LESSON_DIR = Path(__file__).parent
TASK_DIR = LESSON_DIR / "tasks" / "debug-task"


def check_prerequisites() -> bool:
    """Verify Docker and Harbor are available."""
    print("=" * 60)
    print("Checking Prerequisites")
    print("=" * 60)

    docker_ok = shutil.which("docker") is not None
    harbor_ok = shutil.which("harbor") is not None
    result = subprocess.run(
        ["docker", "info"], capture_output=True, text=True,
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


def run_non_interactive_inspection() -> None:
    """Validate the task with the oracle agent."""
    print("=" * 60)
    print("Step 5: Non-Interactive Inspection")
    print("=" * 60)
    print()
    print("You can also validate the environment without entering")
    print("it interactively. Let's run the oracle agent.")
    print()
    print(f"  Running: harbor run -p {TASK_DIR.relative_to(LESSON_DIR)} -a oracle")
    print()
    print("-" * 60)

    result = subprocess.run(
        ["harbor", "run", "-p", str(TASK_DIR), "-a", "oracle"],
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

    print("-" * 60)
    print()

    if result.returncode == 0:
        print("  Task validated successfully.")
    else:
        print(f"  Validation failed (return code {result.returncode}).")
        print("  Use interactive mode to debug the issue.")
    print()


def show_summary() -> None:
    """Display the lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("Interactive environments let you debug Harbor tasks by")
    print("entering the same container where agents work.")
    print()
    print("Key command:")
    print("  harbor task start-env -p <task-dir> -e docker -i")
    print()
    print("Inside the container you can:")
    print("  - Explore the filesystem and installed tools")
    print("  - Run the solution manually")
    print("  - Execute the test script and check the reward")
    print("  - Debug network issues, missing dependencies, etc.")
    print()
    print("The container is automatically deleted when you exit.")
    print()
    print("This completes Module 2: Working with Tasks.")
    print("Next module: Module 3 -- Running Evaluations")


def main() -> None:
    """Run the interactive-env lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Module 2, Lesson 4         #")
    print("#          Debugging with Interactive Environments      #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_interactive_mode()
    show_task_environment(TASK_DIR)
    show_interactive_instructions(LESSON_DIR, TASK_DIR)
    show_debugging_commands()
    run_non_interactive_inspection()
    show_debugging_workflow()
    show_summary()


if __name__ == "__main__":
    main()
