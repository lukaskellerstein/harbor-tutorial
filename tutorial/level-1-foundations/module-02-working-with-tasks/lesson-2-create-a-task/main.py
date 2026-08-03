"""
Lesson 2: Scaffolding a Task

This lesson shows how to create a complete Harbor task from scratch.
We build a "fizzbuzz" task, then validate it by running the oracle agent.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from task_content import ALL_FILES

LESSON_DIR = Path(__file__).parent
TASK_DIR = LESSON_DIR / "tasks" / "fizzbuzz"


def check_prerequisites() -> bool:
    """Verify Docker and Harbor are available."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
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
    print("  All prerequisites met.")
    print()
    return True


def show_harbor_task_init() -> None:
    """Explain the harbor task init command."""
    print("=" * 60)
    print("Step 2: The harbor task init Command")
    print("=" * 60)
    print()
    print("Harbor provides a scaffolding command to create new tasks:")
    print()
    print("  harbor task init <org/task-name>")
    print()
    print("This creates a task directory with all five components:")
    print("  instruction.md, task.toml, environment/Dockerfile,")
    print("  tests/test.sh, solution/solve.sh")
    print()
    print("Useful flags:")
    print("  -p, --tasks-dir   Where to create the task (default: .)")
    print("  --no-pytest       Use a simple bash test.sh instead of pytest")
    print("  --no-solution     Skip the solution directory")
    print("  --steps N         Create a multi-step task with N steps")
    print()
    print("In this lesson, we create a task PROGRAMMATICALLY to see")
    print("exactly what goes into each file. In practice, use")
    print("'harbor task init' to scaffold and then edit the files.")
    print()


def create_task() -> None:
    """Create the fizzbuzz task directory from scratch."""
    print("=" * 60)
    print("Step 3: Creating the FizzBuzz Task")
    print("=" * 60)
    print()

    if TASK_DIR.exists():
        shutil.rmtree(TASK_DIR)
        print("  Cleaned up previous task directory.")

    for subdir in ["environment", "tests", "solution"]:
        (TASK_DIR / subdir).mkdir(parents=True)

    print(f"  Created directory: {TASK_DIR.relative_to(LESSON_DIR)}/")

    for rel_path, content in ALL_FILES.items():
        file_path = TASK_DIR / rel_path
        file_path.write_text(content)
        print(f"    [CREATED] {rel_path}")

    (TASK_DIR / "tests" / "test.sh").chmod(0o755)
    (TASK_DIR / "solution" / "solve.sh").chmod(0o755)
    print()
    print("  Task created successfully!")
    print()
    print("  Final structure:")
    print("  tasks/fizzbuzz/")
    print("  ├── instruction.md")
    print("  ├── task.toml")
    print("  ├── environment/")
    print("  │   └── Dockerfile")
    print("  ├── tests/")
    print("  │   └── test.sh")
    print("  └── solution/")
    print("      └── solve.sh")
    print()


def validate_with_oracle() -> None:
    """Run the task with the oracle agent to validate it works."""
    print("=" * 60)
    print("Step 4: Validating with the Oracle Agent")
    print("=" * 60)
    print()
    print("The oracle agent runs solution/solve.sh inside the container,")
    print("then Harbor runs tests/test.sh to verify. If the reward is 1,")
    print("our task is correctly set up.")
    print()
    print(f"Running: harbor run -p {TASK_DIR.relative_to(LESSON_DIR)} -a oracle")
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
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    print("-" * 60)
    print()

    if result.returncode == 0:
        print("  Validation PASSED! The oracle agent solved the task")
        print("  and the test script confirmed the correct output.")
    else:
        print(f"  Validation FAILED (return code {result.returncode}).")
        print("  Check that Docker is running and review the output above.")
    print()


def show_summary() -> None:
    """Display the lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("You created a complete Harbor task from scratch:")
    print()
    print("  1. instruction.md -- Clear, specific instruction for the agent")
    print("  2. task.toml      -- Name, timeouts, and metadata")
    print("  3. Dockerfile     -- Minimal container with Python pre-installed")
    print("  4. test.sh        -- Verifier that checks output correctness")
    print("  5. solve.sh       -- Reference solution for validation")
    print()
    print("Task creation workflow:")
    print("  1. Write a clear instruction")
    print("  2. Build an environment with the required tools")
    print("  3. Write tests that check the expected outcome")
    print("  4. Write a reference solution")
    print("  5. Validate with: harbor run -p <task> -a oracle")
    print()
    print("Next lesson: lesson-3-test-scripts (writing different types of test scripts)")


def main() -> None:
    """Run the create-a-task lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Module 2, Lesson 2         #")
    print("#          Scaffolding a Task                           #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    show_harbor_task_init()
    create_task()
    validate_with_oracle()
    show_summary()


if __name__ == "__main__":
    main()
