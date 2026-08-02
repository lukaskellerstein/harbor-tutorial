"""
Lesson 3: Viewing Results — Exploring Results

This lesson runs an evaluation and then inspects the jobs/
directory to understand how Harbor stores trial results,
rewards, and agent trajectories.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from results_helpers import inspect_trial_results, print_tree


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

    print(f"  Docker running: {'[OK]' if docker_ok else '[FAIL]'}")
    print(f"  Harbor CLI:     {'[OK]' if harbor_ok else '[FAIL]'}")
    print()

    if not (docker_ok and harbor_ok):
        print("Prerequisites not met. Complete the hello-harbor lesson first.")
    return docker_ok and harbor_ok


def run_evaluation() -> Path | None:
    """Run the hello-world evaluation and return the jobs directory."""
    print("=" * 60)
    print("Step 2: Running an Evaluation")
    print("=" * 60)

    lesson_dir = Path(__file__).parent
    task_path = lesson_dir / "tasks" / "hello-world"

    print(f"\nRunning: harbor run -p {task_path} -a oracle --no-delete --ek keep_containers=true")
    print("(Using the oracle agent to guarantee a successful trial)")
    print()

    result = subprocess.run(
        [
            "harbor",
            "run",
            "-p",
            str(task_path),
            "-a",
            "oracle",
            "--no-delete",
            "--ek",
            "keep_containers=true",
        ],
        capture_output=True,
        text=True,
        cwd=str(lesson_dir),
        check=False,
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        print(f"Evaluation failed (return code {result.returncode}).")
        return None

    print("Evaluation completed successfully!")
    print()

    jobs_dir = lesson_dir / "jobs"
    if jobs_dir.exists():
        return jobs_dir
    return None


def explore_jobs_directory(jobs_dir: Path) -> None:
    """Walk the jobs directory and explain its structure."""
    print("=" * 60)
    print("Step 3: Exploring the Jobs Directory")
    print("=" * 60)
    print()
    print(f"Jobs directory: {jobs_dir}")
    print()
    print("Harbor stores all evaluation results in the jobs/ directory.")
    print("Here is the expected structure:")
    print()
    print("  jobs/")
    print("  └── <job-name>/")
    print("      └── <trial>/")
    print("          ├── config.json       # Trial configuration")
    print("          ├── result.json       # Trial outcome & metrics")
    print("          ├── agent/            # Agent trajectory & logs")
    print("          └── verifier/")
    print("              └── reward.txt    # The reward score (0-1)")
    print()
    print("Actual contents of your jobs/ directory:")
    print()
    print_tree(jobs_dir, prefix="  ", max_depth=4)
    print()


def show_results_viewer() -> None:
    """Explain how to use the Harbor results viewer."""
    print("=" * 60)
    print("Step 5: The Harbor Results Viewer")
    print("=" * 60)
    print()
    print("Harbor includes a web-based results viewer for exploring")
    print("job outcomes interactively.")
    print()
    print("To launch the viewer, run:")
    print()
    print("  harbor view jobs")
    print()
    print("This opens a local web UI where you can:")
    print("  - Browse all jobs and trials")
    print("  - View rewards and success rates")
    print("  - Inspect agent trajectories")
    print("  - Compare agent performance")
    print()
    print("(We are not launching it here to avoid blocking the script.)")
    print("(Try it yourself after this lesson completes!)")
    print()


def show_summary() -> None:
    """Display a summary of what was learned."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("In this lesson you learned how to inspect Harbor results:")
    print()
    print("  1. The jobs/ directory stores all evaluation results")
    print("  2. Each trial has config.json (inputs) and result.json (outputs)")
    print("  3. reward.txt contains the score (0 = fail, 1 = pass)")
    print("  4. The agent/ subdirectory contains the agent's trajectory")
    print("  5. 'harbor view jobs' launches an interactive results viewer")
    print()
    print("Key files:")
    print("  config.json  - What was evaluated (agent, task, environment)")
    print("  result.json  - The outcome (reward, status, duration)")
    print("  reward.txt   - The raw reward value written by the test script")
    print()
    print("Next module: Working with Tasks (creating your own tasks)")


def main() -> None:
    """Run the viewing-results lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Lesson 3                   #")
    print("#          Viewing Results: Exploring Trial Output      #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    jobs_dir = run_evaluation()
    if jobs_dir is None:
        print("Could not find jobs directory after evaluation.")
        print("Check the evaluation output above for errors.")
        sys.exit(1)

    explore_jobs_directory(jobs_dir)
    inspect_trial_results(jobs_dir)
    show_results_viewer()
    show_summary()


if __name__ == "__main__":
    main()
