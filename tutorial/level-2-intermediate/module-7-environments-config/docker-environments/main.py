"""
Lesson 1: Docker Environments

Learn how to craft Dockerfiles for Harbor tasks using three approaches:
simple Ubuntu, language-specific Python, and multi-stage Go builds.
"""

import shutil
import subprocess
import sys
import time
from pathlib import Path

LESSON_DIR = Path(__file__).parent
TASKS_DIR = LESSON_DIR / "tasks"

TASKS = [
    ("ubuntu-task", "Simple Ubuntu Base Image", "ubuntu:24.04"),
    ("python-task", "Language-Specific Python Image", "python:3.12-slim"),
    ("multistage-task", "Multi-Stage Go Build", "golang -> alpine:3.20"),
]


def check_prerequisites() -> bool:
    """Verify Docker and Harbor are available."""
    print("=" * 60)
    print("Checking Prerequisites")
    print("=" * 60)
    docker_ok = shutil.which("docker") is not None
    harbor_ok = shutil.which("harbor") is not None
    if docker_ok:
        docker_ok = subprocess.run(
            ["docker", "info"], capture_output=True, text=True
        ).returncode == 0
    print(f"  Docker: {'[OK]' if docker_ok else '[FAIL] not running'}")
    print(f"  Harbor: {'[OK]' if harbor_ok else '[FAIL] not found'}")
    print()
    return docker_ok and harbor_ok


def show_approaches() -> None:
    """Explain the three Dockerfile approaches."""
    print("=" * 60)
    print("Step 1: Three Dockerfile Approaches for Harbor Tasks")
    print("=" * 60)
    print()
    for i, (name, label, base) in enumerate(TASKS, 1):
        print(f"  {i}. {label}")
        print(f"     Base image: {base}")
        print()


def show_best_practices() -> None:
    """Display Dockerfile best practices for Harbor."""
    print("=" * 60)
    print("Step 2: Dockerfile Best Practices")
    print("=" * 60)
    print()
    practices = [
        "Keep images small — use slim/alpine, --no-install-recommends",
        "Install only what the task needs",
        "Use WORKDIR /app for a predictable agent workspace",
        "Pre-populate test data in the image with COPY or RUN echo",
        "Use multi-stage builds for compiled languages",
        "Clean package caches: rm -rf /var/lib/apt/lists/*",
    ]
    for p in practices:
        print(f"  - {p}")
    print()


def show_dockerfiles() -> None:
    """Display each Dockerfile."""
    print("=" * 60)
    print("Step 3: Examining the Dockerfiles")
    print("=" * 60)
    print()
    for name, label, _ in TASKS:
        dockerfile = TASKS_DIR / name / "environment" / "Dockerfile"
        if dockerfile.exists():
            print(f"--- {label} ---")
            for line in dockerfile.read_text().strip().splitlines():
                print(f"  {line}")
            print()


def run_task(task_name: str, label: str) -> tuple[str, str]:
    """Run a task with oracle and return (status, elapsed)."""
    task_path = TASKS_DIR / task_name
    print(f"  Running: harbor run -p {task_path} -a oracle")
    start = time.time()
    result = subprocess.run(
        ["harbor", "run", "-p", str(task_path), "-a", "oracle"],
        capture_output=True, text=True, cwd=str(LESSON_DIR),
    )
    elapsed = f"{time.time() - start:.1f}s"
    status = "PASS" if result.returncode == 0 else "FAIL"
    if result.stdout:
        for line in result.stdout.strip().splitlines()[-5:]:
            print(f"    {line}")
    if result.returncode != 0 and result.stderr:
        for line in result.stderr.strip().splitlines()[-3:]:
            print(f"    [stderr] {line}")
    print(f"  Result: {status} ({elapsed})")
    print()
    return status, elapsed


def run_all_tasks() -> None:
    """Build and run all three tasks."""
    print("=" * 60)
    print("Step 4: Building & Running Each Environment")
    print("=" * 60)
    print()
    results = []
    for name, label, _ in TASKS:
        print(f"--- {label} ---")
        status, elapsed = run_task(name, label)
        results.append((label, status, elapsed))

    print("=" * 60)
    print("Step 5: Results Summary")
    print("=" * 60)
    print()
    print(f"  {'Task':<32} {'Status':<8} {'Time':<8}")
    print(f"  {'-'*32} {'-'*8} {'-'*8}")
    for label, status, elapsed in results:
        print(f"  {label:<32} {status:<8} {elapsed:<8}")
    print()


def show_summary() -> None:
    """Display key takeaways."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("  1. Ubuntu base: maximum compatibility, larger image")
    print("  2. Python slim: smaller image, Python ready out of the box")
    print("  3. Multi-stage: smallest runtime image, best for compiled code")
    print()
    print("Next lesson: environment-features (exec, file ops, lifecycle)")


def main() -> None:
    """Run the docker-environments lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 2, Module 7          #")
    print("#          Lesson 1: Docker Environments                #")
    print("########################################################")
    print()
    if not check_prerequisites():
        sys.exit(1)
    show_approaches()
    show_best_practices()
    show_dockerfiles()
    run_all_tasks()
    show_summary()


if __name__ == "__main__":
    main()
