"""
Harbor Tutorial — Module 12, Lesson 2: Multi-Container Tasks

Demonstrates how to create Harbor tasks that use Docker Compose to run
multiple services.  Standard tasks use a single Dockerfile, but real-world
scenarios often require databases, message queues, and other infrastructure.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

LESSON_DIR = Path(__file__).resolve().parent
TASK_DIR = LESSON_DIR / "tasks" / "multi-service"


def print_header(title: str) -> None:
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()


def check_prerequisites() -> bool:
    """Check for harbor CLI and Docker."""
    ok = True
    try:
        result = subprocess.run(
            ["harbor", "--version"],
            capture_output=True, text=True, timeout=10,
        )
        print(f"Harbor: {result.stdout.strip()}" if result.returncode == 0
              else "WARNING: harbor CLI error")
        ok = ok and result.returncode == 0
    except FileNotFoundError:
        print("WARNING: harbor CLI not found. Install: uv tool install harbor")
        ok = False
    try:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, timeout=10,
        )
        print("Docker: running" if result.returncode == 0 else "WARNING: Docker not running")
        ok = ok and result.returncode == 0
    except FileNotFoundError:
        print("WARNING: Docker not found")
        ok = False
    return ok


def explain_multi_container() -> None:
    """Explain when and why to use multi-container tasks."""
    print_header("Step 1: Why Multi-Container Tasks?")
    print("Standard Harbor tasks run inside a single Docker container.")
    print("But many real-world tasks need multiple services:")
    print("  - A web API + database")
    print("  - A frontend + backend + cache")
    print("  - A service + message queue + worker")
    print()
    print("Harbor supports this via Docker Compose. Place a")
    print("docker-compose.yaml in the environment/ directory instead")
    print("of (or alongside) a Dockerfile.")


def show_task_structure() -> None:
    """Show the directory structure of the multi-service task."""
    print_header("Step 2: Task Directory Structure")
    structure = [
        "tasks/multi-service/",
        "|-- instruction.md              # Task instructions",
        "|-- task.toml                    # Configuration & metadata",
        "|-- environment/",
        "|   |-- docker-compose.yaml      # Multi-service definition",
        "|   |-- api/",
        "|   |   |-- Dockerfile           # API service container",
        "|   |   |-- app.py               # Flask application",
        "|   |   |-- requirements.txt     # Python dependencies",
        "|   |-- db/",
        "|       |-- init.sql             # Database initialization",
        "|-- tests/",
        "|   |-- test.sh                  # Verification script",
        "|-- solution/",
        "    |-- solve.sh                 # Oracle solution",
    ]
    for line in structure:
        print(f"  {line}")


def show_compose_config() -> None:
    """Display the docker-compose.yaml and explain each service."""
    print_header("Step 3: Docker Compose Configuration")
    compose_path = TASK_DIR / "environment" / "docker-compose.yaml"
    if not compose_path.exists():
        print(f"ERROR: {compose_path} not found")
        return
    print(compose_path.read_text())
    print("Key points:")
    print("  Service 'main' (REQUIRED -- the agent runs here):")
    print("    - Builds from ./api/Dockerfile (Flask application)")
    print("    - Connects to database via DATABASE_URL env var")
    print("    - Waits for database health check before starting")
    print()
    print("  Service 'db' (sidecar -- supporting infrastructure):")
    print("    - Official postgres:16-alpine image")
    print("    - Schema initialized via init.sql")
    print()
    print("  Harbor overlays this with its own compose files for")
    print("  resource limits, env vars, volumes, and egress control.")


def show_file_content(relative_path: str, label: str) -> None:
    """Display a task file's content."""
    print_header(label)
    filepath = TASK_DIR / relative_path
    if not filepath.exists():
        print(f"ERROR: {filepath} not found")
        return
    print(f"File: tasks/multi-service/{relative_path}")
    print()
    print(filepath.read_text())


def explain_service_interaction() -> None:
    """Explain how agents interact with individual services."""
    print_header("Step 6: Agent Interaction with Services")
    print("IMPORTANT: Harbor requires a service named 'main'. This is")
    print("where the agent runs. Other services are 'sidecars'.")
    print()
    print("BaseEnvironment provides service-specific methods:")
    print()
    print('  # Execute in a sidecar')
    print('  result = await environment.service_exec(')
    print('      command="pg_isready", service="db")')
    print()
    print('  # Download file from a sidecar')
    print('  await environment.service_download_file(')
    print('      source_path="/var/log/app.log",')
    print('      target_path="./app.log", service="db")')
    print()
    print('  # Download directory from a sidecar')
    print('  await environment.service_download_dir(')
    print('      source_dir="/app/output/",')
    print('      target_dir="./output/", service="db")')
    print()
    print('  # Stop a sidecar')
    print('  await environment.stop_service(service="db")')
    print()
    print("NOTE: Sidecar execs use sh (not bash) and do not inherit")
    print("the main container's workdir, user, or persistent env.")


def show_running_instructions() -> None:
    """Show how to run this multi-container task."""
    print_header("Step 7: Running Multi-Container Tasks")
    rel = TASK_DIR.relative_to(LESSON_DIR)
    print(f"  # Validate with the oracle agent")
    print(f"  harbor trial start -p {rel} -a oracle \\")
    print(f'      -m "anthropic/claude-sonnet-4-5-20250929"')
    print()
    print(f"  # Run with claude-code")
    print(f"  harbor trial start -p {rel} -a claude-code \\")
    print(f'      -m "anthropic/claude-sonnet-4-5-20250929"')
    print()
    print(f"  # Explore interactively")
    print(f"  harbor task start-env -p {rel} -e docker -i")


def main() -> None:
    print_header("Multi-Container Tasks with Docker Compose")
    print("This lesson demonstrates how to create Harbor tasks that run")
    print("multiple services using Docker Compose.")
    print()
    check_prerequisites()
    explain_multi_container()
    show_task_structure()
    show_compose_config()
    show_file_content("environment/api/app.py", "Step 4: Flask API Service")
    show_file_content("environment/db/init.sql", "Step 5: Database Initialization")
    explain_service_interaction()
    show_running_instructions()

    print_header("Summary")
    print("Multi-container tasks let you evaluate agents on realistic,")
    print("multi-service scenarios:")
    print("  1. Place docker-compose.yaml in environment/")
    print("  2. Name the agent's service 'main' (required by Harbor)")
    print("  3. Use health checks and depends_on for startup ordering")
    print("  4. Interact via service_exec(), service_download_file/dir()")
    print("  5. Test scripts can query any service to verify results")


if __name__ == "__main__":
    main()
