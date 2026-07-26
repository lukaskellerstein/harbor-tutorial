"""
Explanatory text functions for the interactive-env lesson.

Extracted from main.py to keep lesson code under ~200 lines.
"""

from pathlib import Path


def explain_interactive_mode() -> None:
    """Explain what interactive mode is and why it matters."""
    print("=" * 60)
    print("Step 1: What Is Interactive Mode?")
    print("=" * 60)
    print()
    print("When developing a task, you often need to:")
    print("  - Explore the container filesystem")
    print("  - Test commands before putting them in solve.sh")
    print("  - Debug why a test script fails")
    print("  - Verify that tools are installed correctly")
    print()
    print("Harbor's interactive mode starts a task container and")
    print("drops you into a shell inside it. The container has")
    print("the same environment your agent will see, plus the")
    print("solution and test files pre-loaded for debugging.")
    print()
    print("Command:")
    print("  harbor task start-env -p <task-dir> -e docker -i")
    print()
    print("Flags:")
    print("  -p, --path         Path to the task directory")
    print("  -e, --env          Environment type (default: docker)")
    print("  -i, --interactive   Start an interactive shell")
    print("  -a, --all          Include solution/ and tests/ (default)")
    print("  --non-interactive  Start the container without a shell")
    print()


def show_task_environment(task_dir: Path) -> None:
    """Display the task's Dockerfile and explain the environment."""
    print("=" * 60)
    print("Step 2: Our Debug Task Environment")
    print("=" * 60)
    print()
    print("This lesson includes a task with a richer environment.")
    print("The Dockerfile installs extra debugging tools:")
    print()

    dockerfile = task_dir / "environment" / "Dockerfile"
    if dockerfile.exists():
        for line in dockerfile.read_text().strip().splitlines():
            print(f"    {line}")
    print()

    print("  Installed tools:")
    print("    curl     -- HTTP requests from the command line")
    print("    vim      -- Text editor for modifying files")
    print("    git      -- Version control")
    print("    procps   -- Process inspection (ps, top)")
    print("    net-tools -- Network debugging (netstat, ifconfig)")
    print("    requests  -- Python HTTP library")
    print()


def show_interactive_instructions(lesson_dir: Path, task_dir: Path) -> None:
    """Print instructions for the user to run interactively."""
    print("=" * 60)
    print("Step 3: Enter the Container Interactively")
    print("=" * 60)
    print()
    print("To enter the container, run in a separate terminal:")
    print()
    print(f"  cd {lesson_dir}")
    print(f"  harbor task start-env -p {task_dir} -e docker -i")
    print()
    print("This will:")
    print("  1. Build the Docker image from the Dockerfile")
    print("  2. Start the container")
    print("  3. Copy solution/ to /solution and tests/ to /tests")
    print("  4. Drop you into a bash shell inside the container")
    print()


def show_debugging_commands() -> None:
    """Show common debugging commands to run inside the container."""
    print("=" * 60)
    print("Step 4: Useful Debugging Commands")
    print("=" * 60)
    print()
    print("Once inside the container, try these commands:")
    print()
    print("  # Explore the workspace")
    print("  ls -la /app/")
    print("  pwd")
    print()
    print("  # Check available tools")
    print("  python --version")
    print("  which curl")
    print("  pip list")
    print()
    print("  # Run the solution manually")
    print("  bash /solution/solve.sh")
    print("  python /app/fetch_status.py")
    print()
    print("  # Run the test script manually")
    print("  mkdir -p /logs/verifier")
    print("  bash /tests/test.sh")
    print("  cat /logs/verifier/reward.txt")
    print()
    print("  # Check network connectivity")
    print("  curl -I http://example.com")
    print()
    print("  # Exit the container")
    print("  exit")
    print()


def show_debugging_workflow() -> None:
    """Explain the debugging workflow."""
    print("=" * 60)
    print("Step 6: The Debugging Workflow")
    print("=" * 60)
    print()
    print("When a task fails, debug with this workflow:")
    print()
    print("  1. ENTER    harbor task start-env -p <task> -e docker -i")
    print("  2. EXPLORE  ls, cat, which, pip list")
    print("  3. SOLVE    Run solution manually (bash /solution/solve.sh)")
    print("  4. TEST     Run test (bash /tests/test.sh)")
    print("  5. FIX      Edit files, re-run tests")
    print("  6. VALIDATE harbor run -p <task> -a oracle")
    print()
