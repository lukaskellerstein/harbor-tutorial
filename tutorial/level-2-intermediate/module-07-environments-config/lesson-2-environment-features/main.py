"""
Lesson 2: Environment Capabilities

Learn the BaseEnvironment API — exec(), file uploads/downloads,
path checks, and ExecResult handling — then see them in action
through a custom agent.
"""

import shutil
import subprocess
import sys
from pathlib import Path

LESSON_DIR = Path(__file__).parent
TASK_DIR = LESSON_DIR / "tasks" / "env-explore"


def check_prerequisites() -> bool:
    """Verify Docker and Harbor are available."""
    print("=" * 60)
    print("Checking Prerequisites")
    print("=" * 60)
    docker_ok = shutil.which("docker") is not None
    harbor_ok = shutil.which("harbor") is not None
    if docker_ok:
        docker_ok = (
            subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                check=False,
            ).returncode
            == 0
        )
    print(f"  Docker: {'[OK]' if docker_ok else '[FAIL] not running'}")
    print(f"  Harbor: {'[OK]' if harbor_ok else '[FAIL] not found'}")
    print()
    return docker_ok and harbor_ok


def explain_api() -> None:
    """Explain the key methods of BaseEnvironment."""
    print("=" * 60)
    print("Step 1: The BaseEnvironment API")
    print("=" * 60)
    print()
    print("Your custom agent receives a BaseEnvironment object — your")
    print("async interface to the running container.")
    print()
    methods = [
        ("exec(command, cwd, env, timeout_sec, user) -> ExecResult", "Run a shell command inside the container"),
        ("upload_file(source_path, target_path)", "Copy a file from host into the container"),
        ("download_file(source_path, target_path)", "Copy a file from the container to host"),
        ("upload_dir(source_dir, target_dir)", "Copy a directory from host into the container"),
        ("download_dir(source_dir, target_dir)", "Copy a directory from the container to host"),
        ("is_file(path) -> bool", "Check if a container path is a regular file"),
        ("is_dir(path) -> bool", "Check if a container path is a directory"),
    ]
    for sig, desc in methods:
        print(f"  {sig}")
        print(f"       {desc}")
        print()


def explain_exec_result() -> None:
    """Explain the ExecResult model."""
    print("=" * 60)
    print("Step 2: ExecResult — Command Output")
    print("=" * 60)
    print()
    print("  class ExecResult(BaseModel):")
    print("      stdout: str | None    # Standard output")
    print("      stderr: str | None    # Standard error")
    print("      return_code: int      # Exit code (0 = success)")
    print()
    print("  Usage:")
    print('    result = await environment.exec(command="ls /app")')
    print("    if result.return_code == 0:")
    print("        print(result.stdout)")
    print()


def show_agent_highlights() -> None:
    """Show what the EnvironmentExplorerAgent does."""
    print("=" * 60)
    print("Step 3: The EnvironmentExplorerAgent")
    print("=" * 60)
    print()
    print("  agent.py defines a custom agent that demonstrates each method:")
    print()
    print("  1. exec()            — Lists /app/data/ contents")
    print("  2. exec(env=...)     — Passes environment variables")
    print("  3. is_file/is_dir    — Checks whether paths exist")
    print("  4. upload_file()     — Sends a host file into the container")
    print("  5. download_file()   — Retrieves a container file to host")
    print("  6. exec(user='root') — Runs a command as a specific user")
    print()


def show_task_setup() -> None:
    """Show the task that the agent will run against."""
    print("=" * 60)
    print("Step 4: Task Setup")
    print("=" * 60)
    print()
    print("  Pre-populated files in the container:")
    print("    /app/data/config.json   — JSON configuration")
    print("    /app/data/sample.log    — Sample log file")
    print("    /app/data/settings.env  — Key-value settings")
    print()


def run_harbor(label: str, args: list[str]) -> None:
    """Run a harbor command and print results."""
    print(f"  Running: harbor {' '.join(args)}")
    print()
    result = subprocess.run(
        ["harbor"] + args,
        capture_output=True,
        text=True,
        cwd=str(LESSON_DIR),
        check=False,
    )
    if result.stdout:
        for line in result.stdout.strip().splitlines():
            print(f"  {line}")
    if result.stderr:
        for line in result.stderr.strip().splitlines()[-5:]:
            print(f"  [stderr] {line}")
    status = "[OK]" if result.returncode == 0 else f"[FAIL] rc={result.returncode}"
    print(f"\n  {status} {label}")
    print()


def run_evaluations() -> None:
    """Run with oracle, then with the custom explorer agent."""
    print("=" * 60)
    print("Step 5: Validating with Oracle Agent")
    print("=" * 60)
    print()
    run_harbor("Oracle passed", ["run", "-p", str(TASK_DIR), "-a", "oracle"])

    print("=" * 60)
    print("Step 6: Running with EnvironmentExplorerAgent")
    print("=" * 60)
    print()
    run_harbor(
        "Explorer agent completed",
        [
            "run",
            "-p",
            str(TASK_DIR),
            "--agent",
            "agent:EnvironmentExplorerAgent",
        ],
    )


def show_summary() -> None:
    """Display key takeaways."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("  exec()          — Run commands (your primary tool)")
    print("  upload_file()   — Send files into the container")
    print("  download_file() — Retrieve files from the container")
    print("  is_file()       — Check if a file exists")
    print("  is_dir()        — Check if a directory exists")
    print()
    print("  All methods are async. exec() returns ExecResult with")
    print("  stdout, stderr, and return_code.")
    print()
    print("Next lesson: lesson-3-model-routing (LiteLLM format and configuration)")


def main() -> None:
    """Run the environment-features lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 2, Module 7          #")
    print("#          Lesson 2: Environment Capabilities           #")
    print("########################################################")
    print()
    if not check_prerequisites():
        sys.exit(1)
    explain_api()
    explain_exec_result()
    show_agent_highlights()
    show_task_setup()
    run_evaluations()
    show_summary()


if __name__ == "__main__":
    main()
