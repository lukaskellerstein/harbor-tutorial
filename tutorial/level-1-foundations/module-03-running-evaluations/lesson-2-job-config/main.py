"""
Lesson: Job Configuration with job.yaml
========================================
Learn how to configure multi-trial evaluation jobs using job.yaml,
understand each configuration section, and run a job across multiple tasks.
"""

import json
import sys
from pathlib import Path

import yaml

from helpers import (
    check_prerequisites,
    find_latest_dir,
    print_trial_summary,
    run_harbor_command,
)


def explain_job_config() -> None:
    """Walk through the job.yaml configuration file section by section."""
    print("=" * 60)
    print("Step 1: Understanding job.yaml")
    print("=" * 60)
    print("\nA job.yaml file tells Harbor how to run an evaluation job.\n")

    config_text = Path("job.yaml").read_text()
    print("--- job.yaml ---")
    print(config_text)
    print("--- end ---")

    config = yaml.safe_load(config_text) or {}
    if not isinstance(config, dict):
        raise TypeError("job.yaml must have a mapping at the top level")
    print("Section-by-section breakdown:\n")
    print(f"  jobs_dir: {config.get('jobs_dir', 'jobs')}")
    print("    -> Where job results are stored\n")
    print(f"  n_attempts: {config.get('n_attempts', 1)}")
    print("    -> Number of times to attempt each trial (for pass@k)\n")

    orch = config.get("orchestrator", {})
    print(f"  orchestrator.type: {orch.get('type', 'local')}")
    print(f"  orchestrator.n_concurrent_trials: {orch.get('n_concurrent_trials', 1)}")
    print("    -> How many trials run in parallel\n")

    env = config.get("environment", {})
    print(f"  environment.type: {env.get('type', 'docker')}")
    print(f"  environment.force_build: {env.get('force_build', False)}")
    print(f"  environment.delete: {env.get('delete', True)}")
    print("    -> Container runtime and lifecycle settings\n")

    for i, agent in enumerate(config.get("agents", [])):
        print(f"  agents[{i}].name: {agent.get('name', 'N/A')}")
    print("    -> Which agent(s) to evaluate\n")

    for i, ds in enumerate(config.get("datasets", [])):
        print(f"  datasets[{i}].path: {ds.get('path', 'N/A')}")
    print("    -> Path to task directories (Harbor discovers all tasks)\n")


def show_dataset_structure() -> None:
    """Display the tasks that will be run."""
    print("=" * 60)
    print("Step 2: Our dataset (two tasks)")
    print("=" * 60)
    print()

    for task_dir in sorted(Path("tasks").iterdir()):
        if not task_dir.is_dir():
            continue
        instr_path = task_dir / "instruction.md"
        if instr_path.exists():
            first_line = instr_path.read_text().strip().split("\n")[0]
            print(f"  {task_dir.name}/")
            print(f"    Instruction: {first_line}\n")

    print("Harbor will run the agent against each task automatically.\n")


def run_job() -> Path | None:
    """Run the job using harbor run -c job.yaml."""
    print("=" * 60)
    print("Step 3: Running the job with `harbor run -c job.yaml`")
    print("=" * 60)
    print("\nWith n_concurrent_trials=2, both tasks run in parallel.\n")
    print("Running job (this may take a few minutes)...")
    print("-" * 60)

    result = run_harbor_command(["harbor", "run", "-c", "job.yaml", "-y"])

    print("-" * 60)

    if result.returncode != 0:
        print(f"Job failed with exit code {result.returncode}")
        return None

    job_dir = find_latest_dir("jobs")
    if job_dir:
        print(f"\nJob output directory: {job_dir}\n")
    return job_dir


def inspect_job_results(job_dir: Path) -> None:
    """Read and display the job results."""
    print("=" * 60)
    print("Step 4: Inspecting job results")
    print("=" * 60)

    trial_dirs = [d for d in sorted(job_dir.iterdir()) if d.is_dir()]
    print(f"\nThe job produced {len(trial_dirs)} trial(s):\n")

    for trial_dir in trial_dirs:
        print_trial_summary(trial_dir)

    # Job-level result
    job_result_path = job_dir / "result.json"
    if job_result_path.exists():
        print("--- Job Summary ---")
        job_result = json.loads(job_result_path.read_text())
        for key, stats in job_result.get("stats", {}).get("evals", {}).items():
            print(f"  Evaluation: {key}")
            print(f"    Trials: {stats.get('n_trials', 'N/A')}")
            print(f"    Errors: {stats.get('n_errors', 'N/A')}")
            for metric in stats.get("metrics", []):
                for name, val in metric.items():
                    formatted = f"{val:.3f}" if isinstance(val, float) else str(val)
                    print(f"    {name}: {formatted}")
        print()


def explain_alternative_cli() -> None:
    """Show equivalent CLI commands for running jobs."""
    print("=" * 60)
    print("Step 5: Alternative ways to run jobs")
    print("=" * 60)
    print("\nInstead of job.yaml, you can use CLI flags:\n")
    print("  # Local dataset")
    print("  harbor run -p tasks -a oracle --delete\n")
    print("  # Registered dataset with model")
    print("  harbor run -d 'org/dataset' -a claude-code -m anthropic/claude-sonnet-4-5-20250929\n")
    print("  # With concurrency")
    print("  harbor run -p tasks -a oracle -n 4 --delete\n")
    print("  # Multiple attempts (pass@k)")
    print("  harbor run -p tasks -a oracle -k 3 --delete\n")
    print("The job.yaml approach is preferred for reproducible evaluations.\n")


def recap() -> None:
    """Summarize what was learned."""
    print("=" * 60)
    print("Recap")
    print("=" * 60)
    print("\nIn this lesson you learned:\n")
    print("  1. job.yaml configures datasets, agents, environment, and orchestrator")
    print("  2. `harbor run -c job.yaml` runs all trials defined by the config")
    print("  3. Harbor discovers all tasks in the dataset path automatically")
    print("  4. Results are stored in jobs/<timestamp>/<trial-name>/")
    print("  5. CLI flags can substitute for or override job.yaml settings")
    print("\nNext lesson: Built-in Agents\n")


def main() -> None:
    """Run the job-config lesson."""
    print()
    print("=" * 60)
    print("  Harbor Tutorial - Module 3, Lesson 2")
    print("  Job Configuration with job.yaml")
    print("=" * 60)
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_job_config()
    show_dataset_structure()

    job_dir = run_job()
    if job_dir is None:
        print("Could not complete the job. Check the errors above.")
        sys.exit(1)

    inspect_job_results(job_dir)
    explain_alternative_cli()
    recap()


if __name__ == "__main__":
    main()
