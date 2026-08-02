"""
Lesson 2: Using Registered Datasets

Registered datasets live in the Harbor registry and can be referenced by name
with the -d flag. This lesson explores the registry, explains the naming
convention, and demonstrates the CLI commands for working with registered
datasets.
"""

import shutil
import subprocess
import sys

from examples import show_dataset_download, show_job_config_example, show_run_examples


def check_prerequisites() -> bool:
    """Verify Harbor is available."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
    print("=" * 60)

    harbor_ok = shutil.which("harbor") is not None
    docker_ok = shutil.which("docker") is not None

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

    if not harbor_ok:
        print("Harbor CLI is required. Install with: uv tool install harbor")
        return False
    return True


def explain_registry_concept() -> None:
    """Explain the dataset registry and naming convention."""
    print("=" * 60)
    print("Step 2: The Harbor Dataset Registry")
    print("=" * 60)
    print()
    print("The Harbor registry is a central repository of published datasets")
    print("and tasks. It works similarly to package registries like PyPI or")
    print("npm -- authors publish datasets, and users reference them by name.")
    print()
    print("Dataset naming convention:")
    print("  org/dataset-name          Latest version")
    print("  org/dataset-name@v1.0     Specific version")
    print("  org/dataset-name@head     Latest development version")
    print()
    print("Examples:")
    print("  harbor/hello-world        Harbor's official hello-world dataset")
    print("  swe-bench/verified        SWE-bench Verified benchmark")
    print("  terminal-bench/v1         Terminal-Bench v1")
    print()
    print("The registry supports:")
    print("  - Versioned datasets with semantic versioning")
    print("  - Public and private visibility")
    print("  - Automatic download and caching")
    print("  - Git-based and HTTP-based registries")
    print()


def list_registered_datasets() -> None:
    """Run harbor dataset list and display results."""
    print("=" * 60)
    print("Step 3: Listing Registered Datasets")
    print("=" * 60)
    print()
    print("The 'harbor dataset list' command shows available datasets.")
    print("By default, it prints a link to the Harbor registry website.")
    print("Use --legacy for a table-based listing.")
    print()
    print("Running: harbor dataset list")
    print("-" * 60)

    result = subprocess.run(
        ["harbor", "dataset", "list"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    print("-" * 60)
    print()

    print("Running: harbor dataset list --legacy")
    print("(This fetches the full dataset listing from the registry)")
    print("-" * 60)

    result = subprocess.run(
        ["harbor", "dataset", "list", "--legacy"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        stderr_lines = result.stderr.strip().split("\n")
        for line in stderr_lines:
            if line.strip():
                print(f"  {line}")

    print("-" * 60)
    print()


def explain_d_vs_p_flags() -> None:
    """Explain the difference between -d and -p flags."""
    print("=" * 60)
    print("Step 4: Local (-p) vs Registered (-d) Datasets")
    print("=" * 60)
    print()
    print("Harbor provides two ways to specify a dataset:")
    print()
    print("  -p / --path     Point to a local dataset directory")
    print("  -d / --dataset  Reference a registered dataset by name")
    print()
    print("Examples:")
    print()
    print("  # Local dataset (directory on your filesystem)")
    print("  harbor run -p ./my-tasks -a oracle")
    print()
    print("  # Registered dataset (downloaded from registry)")
    print('  harbor run -d "harbor/hello-world" -a oracle')
    print()
    print("  # Registered dataset with model specification")
    print('  harbor run -d "harbor/hello-world" -a claude-code \\')
    print('    -m "anthropic/claude-sonnet-4-5-20250929"')
    print()
    print("When you use -d, Harbor:")
    print("  1. Resolves the dataset name in the registry")
    print("  2. Downloads the task files (if not already cached)")
    print("  3. Caches them locally (~/.cache/harbor/tasks/)")
    print("  4. Runs the evaluation against the cached tasks")
    print()


def show_summary() -> None:
    """Display lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("In this lesson you learned:")
    print("  1. The Harbor registry hosts published datasets and tasks")
    print("  2. Datasets use org/name@version naming convention")
    print("  3. 'harbor dataset list' browses available datasets")
    print("  4. -d references registered datasets, -p references local ones")
    print("  5. Registered datasets are automatically downloaded and cached")
    print("  6. 'harbor dataset download' lets you inspect task files locally")
    print("  7. Both local and registered datasets work in job.yaml configs")
    print()
    print("Next lesson: lesson-3-task-metadata")
    print("  (Deep dive into task.toml configuration)")


def main() -> None:
    """Run the registered-datasets lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 2, Module 6          #")
    print("#          Lesson 2: Using Registered Datasets          #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_registry_concept()
    list_registered_datasets()
    explain_d_vs_p_flags()
    show_dataset_download()
    show_run_examples()
    show_job_config_example()
    show_summary()


if __name__ == "__main__":
    main()
