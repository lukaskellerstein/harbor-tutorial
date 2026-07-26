"""
Lesson 1: Hello Harbor — Installation & First Run

This lesson verifies that your environment is set up correctly
and runs your very first Harbor evaluation using the oracle agent.
"""

import shutil
import subprocess
import sys
from pathlib import Path


def check_python_version() -> bool:
    """Check that Python 3.12+ is installed."""
    version = sys.version_info
    print(f"  Python version: {version.major}.{version.minor}.{version.micro}")
    if version >= (3, 12):
        print("  [OK] Python 3.12+ detected")
        return True
    else:
        print("  [FAIL] Python 3.12+ is required")
        return False


def check_docker_running() -> bool:
    """Check that Docker is installed and the daemon is running."""
    if not shutil.which("docker"):
        print("  [FAIL] Docker CLI not found. Install Docker Desktop.")
        return False

    result = subprocess.run(
        ["docker", "info"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("  [OK] Docker is installed and running")
        return True
    else:
        print("  [FAIL] Docker daemon is not running. Start Docker Desktop.")
        return False


def check_harbor_installed() -> bool:
    """Check that the Harbor CLI is available."""
    if shutil.which("harbor"):
        result = subprocess.run(
            ["harbor", "--version"],
            capture_output=True,
            text=True,
        )
        version_str = result.stdout.strip() or result.stderr.strip()
        print(f"  Harbor version: {version_str}")
        print("  [OK] Harbor CLI is installed")
        return True
    else:
        print("  [FAIL] Harbor CLI not found.")
        print("  Install with: uv tool install harbor")
        return False


def check_prerequisites() -> bool:
    """Run all prerequisite checks."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
    print("=" * 60)

    python_ok = check_python_version()
    docker_ok = check_docker_running()
    harbor_ok = check_harbor_installed()

    all_ok = python_ok and docker_ok and harbor_ok
    print()
    if all_ok:
        print("All prerequisites met! Ready to run your first evaluation.")
    else:
        print("Some prerequisites are missing. Please fix the issues above.")
    print()
    return all_ok


def show_task_structure() -> None:
    """Display the hello-world task directory structure."""
    print("=" * 60)
    print("Step 2: Understanding the Hello World Task")
    print("=" * 60)

    task_dir = Path(__file__).parent / "tasks" / "hello-world"
    print(f"\nTask directory: {task_dir}\n")
    print("Directory structure:")
    print("  tasks/hello-world/")
    print("  ├── instruction.md      # What the agent must do")
    print("  ├── task.toml           # Task configuration")
    print("  ├── environment/")
    print("  │   └── Dockerfile      # Container the agent works in")
    print("  ├── tests/")
    print("  │   └── test.sh         # Verifier script (produces reward)")
    print("  └── solution/")
    print("      └── solve.sh        # Reference solution")

    instruction_file = task_dir / "instruction.md"
    if instruction_file.exists():
        print(f"\nInstruction ({instruction_file.name}):")
        print(f'  "{instruction_file.read_text().strip()}"')

    print()


def run_evaluation() -> None:
    """Run the hello-world evaluation using the oracle agent."""
    print("=" * 60)
    print("Step 3: Running Your First Evaluation")
    print("=" * 60)

    task_path = Path(__file__).parent / "tasks" / "hello-world"
    print(f"\nRunning: harbor run -p {task_path} -a oracle")
    print("  Agent: oracle (runs the reference solution)")
    print("  Task:  hello-world (create a file with 'Hello, world!')")
    print()
    print("This will:")
    print("  1. Build a Docker container from the Dockerfile")
    print("  2. Run the oracle agent (executes solution/solve.sh)")
    print("  3. Run the test script (tests/test.sh)")
    print("  4. Report the reward (0 = fail, 1 = pass)")
    print()
    print("-" * 60)

    result = subprocess.run(
        ["harbor", "run", "-p", str(task_path), "-a", "oracle"],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent),
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    print("-" * 60)

    if result.returncode == 0:
        print("\nEvaluation completed successfully!")
    else:
        print(f"\nEvaluation failed with return code {result.returncode}")
        print("Make sure Docker is running and try again.")


def show_summary() -> None:
    """Display a summary of what was learned."""
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("Congratulations! You just ran your first Harbor evaluation.")
    print()
    print("What happened:")
    print("  1. Harbor built a Docker container from the task's Dockerfile")
    print("  2. The oracle agent ran the reference solution (solve.sh)")
    print("  3. The verifier ran the test script (test.sh)")
    print("  4. The test checked for hello.txt and wrote a reward")
    print()
    print("Key concepts introduced:")
    print("  - Task:        A unit of evaluation (instruction + environment + test)")
    print("  - Agent:       A program that attempts to solve a task")
    print("  - Oracle:      A special agent that runs the reference solution")
    print("  - Reward:      A score from 0 to 1 indicating success")
    print("  - Environment: The Docker container where the agent works")
    print()
    print("Next lesson: core-concepts (understanding Harbor's building blocks)")


def main() -> None:
    """Run the hello-harbor lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Lesson 1                   #")
    print("#          Hello Harbor: Installation & First Run       #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    show_task_structure()
    run_evaluation()
    show_summary()


if __name__ == "__main__":
    main()
