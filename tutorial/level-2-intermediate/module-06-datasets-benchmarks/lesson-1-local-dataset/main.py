"""
Lesson 1: Creating a Local Dataset

A dataset in Harbor is simply a directory containing one or more task
subdirectories. This lesson creates a dataset with three tasks of varying
difficulty, runs all of them at once, and displays per-task results.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from results import display_results

LESSON_DIR = Path(__file__).parent
TASKS_DIR = LESSON_DIR / "tasks"


def check_prerequisites() -> bool:
    """Verify Docker and Harbor are available."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
    print("=" * 60)

    docker_ok = shutil.which("docker") is not None
    harbor_ok = shutil.which("harbor") is not None

    if docker_ok:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            check=False,
        )
        docker_ok = result.returncode == 0

    print(f"  Docker:  {'[OK]' if docker_ok else '[FAIL] Docker daemon not running'}")
    print(f"  Harbor:  {'[OK]' if harbor_ok else '[FAIL] Install with: uv tool install harbor'}")
    print()

    if not (docker_ok and harbor_ok):
        print("Prerequisites not met. Please fix the issues above.")
        return False
    return True


def explain_dataset_concept() -> None:
    """Explain what a dataset is in Harbor."""
    print("=" * 60)
    print("Step 2: What Is a Dataset?")
    print("=" * 60)
    print()
    print("A dataset in Harbor is a directory containing task subdirectories.")
    print("There is no special manifest or configuration file for the dataset")
    print("itself -- Harbor discovers tasks by scanning for directories that")
    print("contain a task.toml file.")
    print()
    print("Key points:")
    print("  - A dataset = a directory with one or more task subdirectories")
    print("  - Each task subdirectory must have: task.toml, instruction.md,")
    print("    environment/Dockerfile, tests/test.sh")
    print("  - The -p flag points Harbor at a local dataset path")
    print("  - The -d flag references a registered (remote) dataset")
    print()


def show_dataset_structure() -> None:
    """Display the dataset directory structure."""
    print("=" * 60)
    print("Step 3: Our Dataset Structure")
    print("=" * 60)
    print()
    print(f"Dataset path: {TASKS_DIR}")
    print()
    print("tasks/                          <-- this is the dataset")
    print("├── easy-hello/                 <-- task 1 (easy)")
    print("│   ├── instruction.md")
    print("│   ├── task.toml")
    print("│   ├── environment/Dockerfile")
    print("│   ├── tests/test.sh")
    print("│   └── solution/solve.sh")
    print("├── medium-reverse/             <-- task 2 (medium)")
    print("│   ├── instruction.md")
    print("│   ├── task.toml")
    print("│   ├── environment/Dockerfile")
    print("│   ├── tests/test.sh")
    print("│   └── solution/solve.sh")
    print("└── hard-fibonacci/             <-- task 3 (hard)")
    print("    ├── instruction.md")
    print("    ├── task.toml")
    print("    ├── environment/Dockerfile")
    print("    ├── tests/test.sh")
    print("    └── solution/solve.sh")
    print()

    for task_name in ["easy-hello", "medium-reverse", "hard-fibonacci"]:
        instruction_path = TASKS_DIR / task_name / "instruction.md"
        if instruction_path.exists():
            text = instruction_path.read_text().strip().split("\n")[0]
            print(f"  {task_name}: {text}")
    print()


def run_dataset_evaluation() -> None:
    """Run the entire dataset with the oracle agent."""
    print("=" * 60)
    print("Step 4: Running the Dataset Evaluation")
    print("=" * 60)
    print()
    print("When you pass a directory to 'harbor run -p', Harbor scans it")
    print("for task subdirectories and evaluates each one.")
    print()
    print(f"Running: harbor run -p {TASKS_DIR} -a oracle")
    print()
    print("  -p {path}  : path to a local dataset (directory of tasks)")
    print("  -a oracle  : use the oracle agent (runs solution/solve.sh)")
    print()
    print("The oracle agent is perfect for validating your tasks because")
    print("it runs the reference solution -- if it doesn't score 1.0,")
    print("your task or test script has a bug.")
    print()
    print("-" * 60)

    result = subprocess.run(
        ["harbor", "run", "-p", str(TASKS_DIR), "-a", "oracle"],
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
        print("Dataset evaluation completed successfully!")
    else:
        print(f"Evaluation failed with return code {result.returncode}")
    print()


def show_summary() -> None:
    """Display lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("In this lesson you learned:")
    print("  1. A dataset is simply a directory of task subdirectories")
    print("  2. Harbor discovers tasks by scanning for task.toml files")
    print("  3. Use 'harbor run -p <path>' to evaluate a local dataset")
    print("  4. The oracle agent validates tasks by running solution scripts")
    print("  5. Results include per-task rewards and aggregate metrics")
    print()
    print("Next lesson: lesson-2-registered-datasets")
    print("  (Using public benchmark datasets from the Harbor registry)")


def main() -> None:
    """Run the local-dataset lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 2, Module 6          #")
    print("#          Lesson 1: Creating a Local Dataset           #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_dataset_concept()
    show_dataset_structure()
    run_dataset_evaluation()
    display_results(LESSON_DIR)
    show_summary()


if __name__ == "__main__":
    main()
