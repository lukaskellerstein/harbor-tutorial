"""
Lesson 1: Custom External Agent (BaseAgent)

This lesson teaches how to build a custom agent that runs outside
the container and sends commands in via environment.exec().
"""

import shutil
import subprocess
import sys
from pathlib import Path

LESSON_DIR = Path(__file__).parent


def check_prerequisites() -> bool:
    """Verify Docker and Harbor are available."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
    print("=" * 60)

    docker_ok = shutil.which("docker") is not None
    harbor_ok = shutil.which("harbor") is not None

    if docker_ok:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, text=True,
            check=False,
        )
        docker_ok = result.returncode == 0

    print(f"  Docker: {'[OK]' if docker_ok else '[FAIL] Docker must be running'}")
    print(f"  Harbor: {'[OK]' if harbor_ok else '[FAIL] Install with: uv tool install harbor'}")
    print()

    if not (docker_ok and harbor_ok):
        print("Please fix the issues above before continuing.")
        return False

    print("All prerequisites met!")
    print()
    return True


def explain_base_agent() -> None:
    """Explain what BaseAgent is and how it works."""
    print("=" * 60)
    print("Step 2: Understanding BaseAgent")
    print("=" * 60)
    print()
    print("Harbor has two types of custom agents:")
    print()
    print("  1. External Agent (BaseAgent)")
    print("     - Runs OUTSIDE the container, on the host machine")
    print("     - Sends commands INTO the container via environment.exec()")
    print("     - Simplest agent type — great for wrapping CLI tools")
    print()
    print("  2. Installed Agent (BaseInstalledAgent)")
    print("     - Installs itself INSIDE the container")
    print("     - Runs within the container environment")
    print("     - More complex — covered in the next lesson")
    print()
    print("In this lesson, we build an External Agent (BaseAgent).")
    print()
    print("The BaseAgent lifecycle:")
    print("  1. __init__()  — Harbor creates the agent instance")
    print("  2. setup()     — Prepare the agent (install tools, etc.)")
    print("  3. run()       — Execute the task using environment.exec()")
    print()
    print("Key method — environment.exec(command):")
    print("  - Runs a shell command inside the container")
    print("  - Returns ExecResult with: stdout, stderr, return_code")
    print("  - The agent never enters the container — it sends commands in")
    print()


def show_agent_code() -> None:
    """Display the agent source code."""
    print("=" * 60)
    print("Step 3: The GrepAgent Code")
    print("=" * 60)
    print()

    agent_file = LESSON_DIR / "agent.py"
    if agent_file.exists():
        print(f"File: {agent_file.name}")
        print("-" * 60)
        print(agent_file.read_text())
        print("-" * 60)
    else:
        print(f"  [ERROR] {agent_file} not found")

    print()
    print("Required methods:")
    print("  name()    -> str        # Unique agent identifier")
    print("  version() -> str | None # Agent version")
    print("  setup()                 # Called once before run()")
    print("  run()                   # Execute the task")
    print()


def show_task_structure() -> None:
    """Display the task directory structure."""
    print("=" * 60)
    print("Step 4: Task Structure")
    print("=" * 60)
    print()

    task_dir = LESSON_DIR / "tasks" / "write-file"
    print(f"Task directory: {task_dir.relative_to(LESSON_DIR)}")
    print()
    print("  tasks/write-file/")
    print("  ├── instruction.md      # What the agent must do")
    print("  ├── task.toml           # Task configuration")
    print("  ├── environment/")
    print("  │   └── Dockerfile      # Container definition")
    print("  ├── tests/")
    print("  │   └── test.sh         # Verifier (writes reward 0-1)")
    print("  └── solution/")
    print("      └── solve.sh        # Reference solution")

    instruction_file = task_dir / "instruction.md"
    if instruction_file.exists():
        print()
        print(f"Instruction ({instruction_file.name}):")
        print(f'  "{instruction_file.read_text().strip()}"')

    print()


def run_evaluation() -> None:
    """Run the evaluation with our custom agent."""
    print("=" * 60)
    print("Step 5: Running the Evaluation")
    print("=" * 60)
    print()
    print("Command: harbor run -p tasks/write-file -a agent:GrepAgent")
    print()
    print("This tells Harbor:")
    print("  -p tasks/write-file   Use our local task")
    print("  -a agent:GrepAgent    Use agent.py, class GrepAgent")
    print()
    print("Harbor will:")
    print("  1. Build a Docker container from the Dockerfile")
    print("  2. Instantiate our GrepAgent")
    print("  3. Call agent.setup() then agent.run()")
    print("  4. Run the test script (tests/test.sh)")
    print("  5. Report the reward (0 = fail, 1 = pass)")
    print()
    print("-" * 60)

    task_path = LESSON_DIR / "tasks" / "write-file"
    result = subprocess.run(
        ["harbor", "run", "-p", str(task_path), "-a", "agent:GrepAgent"],
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

    if result.returncode == 0:
        print("\nEvaluation completed successfully!")
    else:
        print(f"\nEvaluation failed with return code {result.returncode}")
        print("Make sure Docker is running and try again.")

    print()


def show_results() -> None:
    """Check the jobs directory for results."""
    print("=" * 60)
    print("Step 6: Inspecting Results")
    print("=" * 60)
    print()

    jobs_dir = LESSON_DIR / "jobs"
    if not jobs_dir.exists():
        print("No jobs/ directory found — the evaluation may not have run.")
        print("You can also run: harbor view jobs")
        print()
        return

    job_dirs = sorted(jobs_dir.iterdir())
    if not job_dirs:
        print("No job results found.")
        print()
        return

    latest_job = job_dirs[-1]
    print(f"Latest job: {latest_job.name}")
    print()

    # Look for result files
    for result_file in sorted(latest_job.rglob("result.json")):
        print(f"  Result: {result_file.relative_to(jobs_dir)}")
        print(f"  Contents: {result_file.read_text()[:500]}")
        print()

    print("Tip: Run 'harbor view jobs' to explore results interactively.")
    print()


def show_summary() -> None:
    """Display a summary of what was learned."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("You just built and ran a custom Harbor agent!")
    print()
    print("Key takeaways:")
    print("  - BaseAgent runs OUTSIDE the container, sends commands IN")
    print("  - Must implement: name(), version(), setup(), run()")
    print("  - environment.exec() returns ExecResult (stdout, stderr, return_code)")
    print("  - context.metadata stores agent execution metadata")
    print("  - Run with: harbor run -p <task> -a module:ClassName")
    print()
    print("Agent reference:")
    print("  from harbor.agents.base import BaseAgent")
    print("  from harbor.environments.base import BaseEnvironment")
    print("  from harbor.models.agent.context import AgentContext")
    print()
    print("Next lesson: lesson-2-installed-agent")
    print("  Build agents that install themselves inside the container")
    print("  using BaseInstalledAgent, exec_as_root(), and exec_as_agent().")


def main() -> None:
    """Run the external-agent lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Module 4, Lesson 1         #")
    print("#     Custom External Agent (BaseAgent)                 #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_base_agent()
    show_agent_code()
    show_task_structure()
    run_evaluation()
    show_results()
    show_summary()


if __name__ == "__main__":
    main()
