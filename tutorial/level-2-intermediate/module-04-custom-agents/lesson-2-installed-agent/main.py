"""
Lesson 2: Custom Installed Agent (BaseInstalledAgent)

Learn how to build an installed agent that lives inside the container,
installs its own tools, and runs commands as the container user.
"""

import shutil
import subprocess
import sys
from pathlib import Path

LESSON_DIR = Path(__file__).parent


def check_prerequisites() -> bool:
    """Verify Docker and Harbor are available."""
    print("=" * 60)
    print("Step 0: Checking Prerequisites")
    print("=" * 60)
    print()

    docker_ok = shutil.which("docker") is not None
    harbor_ok = shutil.which("harbor") is not None

    if docker_ok:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, text=True,
            check=False,
        )
        docker_ok = result.returncode == 0

    print(f"  Docker installed and running: {'[OK]' if docker_ok else '[FAIL]'}")
    print(f"  Harbor CLI installed:         {'[OK]' if harbor_ok else '[FAIL]'}")
    print()

    if not docker_ok:
        print("  Docker must be installed and running. Start Docker Desktop.")
    if not harbor_ok:
        print("  Install Harbor: uv tool install harbor")

    return docker_ok and harbor_ok


def explain_installed_agent() -> None:
    """Step 1: Explain what a BaseInstalledAgent is."""
    print("=" * 60)
    print("Step 1: What Is a BaseInstalledAgent?")
    print("=" * 60)
    print()
    print("  A BaseInstalledAgent installs itself INSIDE the task container,")
    print("  then runs there as a local process.")
    print()
    print("  Key methods:")
    print("    install(env)  -- exec_as_root() for system pkgs, exec_as_agent() for tools")
    print("    run(instruction, env, ctx) -- Solve the task with exec_as_agent()")
    print()
    print("  Lifecycle: setup() -> install() -> run()")
    print("  Most built-in agents (claude-code, openhands, aider) work this way.")
    print()


def compare_agent_types() -> None:
    """Step 2: Compare BaseAgent vs BaseInstalledAgent."""
    print("=" * 60)
    print("Step 2: BaseAgent vs BaseInstalledAgent")
    print("=" * 60)
    print()
    print("  BaseAgent (external)        | BaseInstalledAgent (installed)")
    print("  ----------------------------+-------------------------------")
    print("  Runs OUTSIDE container      | Runs INSIDE container")
    print("  Uses environment.exec()     | Uses exec_as_agent()")
    print("  No install step             | Has install() for setup")
    print("  Good for API-based agents   | Good for CLI tools / packages")
    print()


def show_agent_code() -> None:
    """Step 3: Show the agent implementation."""
    print("=" * 60)
    print("Step 3: The ShellScriptAgent Implementation")
    print("=" * 60)
    print()

    agent_file = LESSON_DIR / "agent.py"
    if agent_file.exists():
        code = agent_file.read_text()
        print(code)
    else:
        print("  [ERROR] agent.py not found!")
    print()


def show_task_structure() -> None:
    """Step 4: Show the task directory structure."""
    print("=" * 60)
    print("Step 4: Task Structure")
    print("=" * 60)
    print()
    print("  tasks/parse-json/")
    print("  ├── instruction.md      # Extract 'result' from JSON")
    print("  ├── task.toml           # Task configuration")
    print("  ├── environment/Dockerfile  # python:3.12-slim with data.json")
    print("  ├── tests/test.sh       # Checks output.txt == 42")
    print("  └── solution/solve.sh   # Reference solution")

    instruction_file = LESSON_DIR / "tasks" / "parse-json" / "instruction.md"
    if instruction_file.exists():
        print(f'\n  Instruction:\n    "{instruction_file.read_text().strip()}"')
    print()


def run_evaluation() -> None:
    """Step 5: Run the evaluation with our custom installed agent."""
    print("=" * 60)
    print("Step 5: Running the Evaluation")
    print("=" * 60)
    print()

    task_path = LESSON_DIR / "tasks" / "parse-json"
    cmd = ["harbor", "run", "-p", str(task_path), "-a", "agent:ShellScriptAgent"]

    print(f"  Command: {' '.join(cmd)}")
    print()
    print("  Harbor will: build container -> install() -> run() -> verify")
    print()
    print("-" * 60)

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(LESSON_DIR), check=False
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    print("-" * 60)

    if result.returncode == 0:
        print("\n  Evaluation completed successfully!")
    else:
        print(f"\n  Evaluation failed (exit code {result.returncode}).")
        print("  Make sure Docker is running and try again.")
    print()


def show_results() -> None:
    """Step 6: Display and explain the results."""
    print("=" * 60)
    print("Step 6: Understanding the Results")
    print("=" * 60)
    print()
    print("  Results are stored in jobs/. A reward of 1.0 means the agent")
    print("  successfully extracted '42' from data.json into output.txt.")

    jobs_dir = LESSON_DIR / "jobs"
    if jobs_dir.exists():
        result_files = sorted(jobs_dir.rglob("result.json"))
        if result_files:
            latest = result_files[-1]
            print(f"\n  Latest result: {latest}")
            print(f"  {latest.read_text().strip()}")
    print()


def show_summary() -> None:
    """Print key takeaways."""
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("  You built a BaseInstalledAgent that:")
    print("    1. Installed jq inside the container (exec_as_root)")
    print("    2. Created a helper script (exec_as_agent)")
    print("    3. Used the script to parse JSON and extract a value")
    print()
    print("  Key takeaways:")
    print("    - BaseInstalledAgent installs itself inside the container")
    print("    - install() runs before run() -- use it for setup")
    print("    - exec_as_root for system packages (apt-get)")
    print("    - exec_as_agent for user-level commands")
    print("    - @with_prompt_template enables Jinja2 prompt rendering")
    print("    - Most built-in Harbor agents are installed agents")
    print()
    print("  Next lesson: lesson-3-prompt-templates")
    print("    Structure agent prompts with Jinja2 templates")
    print()


def main() -> None:
    """Run the installed-agent lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Module 4, Lesson 2         #")
    print("#     Custom Installed Agent (BaseInstalledAgent)       #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_installed_agent()
    compare_agent_types()
    show_agent_code()
    show_task_structure()
    run_evaluation()
    show_results()
    show_summary()


if __name__ == "__main__":
    main()
