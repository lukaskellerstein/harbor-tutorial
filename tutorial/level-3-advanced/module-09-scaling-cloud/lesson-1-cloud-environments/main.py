"""
Lesson 1: Cloud Sandbox Environments

Learn about Harbor's 20+ environment providers and when to use
cloud sandboxes instead of local Docker for evaluations.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from providers import ENVIRONMENT_TYPES, get_job_configs, write_job_config


def check_prerequisites() -> bool:
    """Verify Harbor CLI is available."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
    print("=" * 60)

    if not shutil.which("harbor"):
        print("  [FAIL] Harbor CLI not found. Install with: uv tool install harbor")
        return False

    result = subprocess.run(["harbor", "--version"], capture_output=True, text=True)
    version = result.stdout.strip() or result.stderr.strip()
    print(f"  Harbor version: {version}")
    print("  [OK] Harbor CLI is installed")
    print()
    return True


def list_environment_types() -> None:
    """Display all supported environment types grouped by category."""
    print("=" * 60)
    print("Step 2: Supported Environment Types")
    print("=" * 60)

    categories: dict[str, list[tuple[str, dict[str, str]]]] = {}
    for name, info in ENVIRONMENT_TYPES.items():
        cat = info["category"]
        categories.setdefault(cat, []).append((name, info))

    print(f"\nHarbor supports {len(ENVIRONMENT_TYPES)} environment providers:\n")
    for category, entries in categories.items():
        print(f"  [{category}] ({len(entries)} providers)")
        for name, info in entries:
            print(f"    - {name:20s} {info['description']}")
        print()


def explain_cloud_vs_local() -> None:
    """Explain when to use cloud vs local Docker."""
    print("=" * 60)
    print("Step 3: When to Use Cloud vs Local Docker")
    print("=" * 60)
    print("""
  LOCAL DOCKER (default)
    Best for: development, testing, small runs (1-10 tasks)
    Limitations: CPU-bound, typically 2-4 concurrent trials max
    CLI: harbor run -d <dataset> -a <agent>

  CLOUD SANDBOXES (daytona, modal, e2b, etc.)
    Best for: large-scale evals (50-500+ tasks), production benchmarks
    Advantages: I/O-bound, scale to 32-128+ concurrent trials
    CLI: harbor run -d <dataset> -a <agent> -e daytona -n 32
""")


def generate_job_configs() -> None:
    """Generate and display example job configs for different providers."""
    print("=" * 60)
    print("Step 4: Job Configurations for Cloud Providers")
    print("=" * 60)

    configs_dir = Path(__file__).parent / "configs"
    for filename, config in get_job_configs().items():
        write_job_config(configs_dir, filename, config)
        print(f"\n  Generated: configs/{filename}")
        print(f"  Provider:  {config['environment']['type']}")
        print(f"  Parallel:  {config['n_concurrent_trials']} concurrent trials")
        print("  ---")
        for line in yaml.dump(config, default_flow_style=False, sort_keys=False).splitlines():
            print(f"    {line}")
    print()


def explain_environment_kwargs() -> None:
    """Explain provider-specific kwargs in environment config."""
    print("=" * 60)
    print("Step 5: Environment Kwargs (Provider-Specific Options)")
    print("=" * 60)
    print("""
  Each cloud provider accepts additional kwargs:

    environment:
      type: daytona
      kwargs:
        target: us-east-1           # Provider-specific options

  Resource overrides (work with any provider):
    environment:
      type: modal
      override_cpus: 4              # Request 4 CPUs
      override_memory_mb: 8192      # Request 8 GB RAM
      override_storage_mb: 20480    # Request 20 GB storage
""")


def show_cli_syntax() -> None:
    """Show CLI syntax for running with different providers."""
    print("=" * 60)
    print("Step 6: CLI Syntax for Cloud Providers")
    print("=" * 60)
    print("""
  The -e (--environment) flag selects the provider:

  harbor run -d <dataset> -a <agent>                  # Docker (default)
  harbor run -d <dataset> -a <agent> -e daytona       # Daytona
  harbor run -d <dataset> -a <agent> -e modal         # Modal
  harbor run -d <dataset> -a <agent> -e e2b           # E2B
  harbor run -d <dataset> -a <agent> -e daytona -n 32 # Cloud + parallel
  harbor run -c configs/daytona-job.yaml              # From job config
""")


def discuss_cost_and_setup() -> None:
    """Discuss cost and setup requirements."""
    print("=" * 60)
    print("Step 7: Cost and Setup Considerations")
    print("=" * 60)
    print("""
  1. DOCKER (Free) — Install Docker Desktop, no API keys needed
  2. DAYTONA — Set DAYTONA_API_KEY, charged per sandbox-minute
  3. MODAL — Run `modal token new`, free tier ~$30/month
  4. E2B — Set E2B_API_KEY, free tier available
  5. EC2 — Configure AWS credentials, standard pricing

  Tips: Start with Docker for dev. Use cloud for full benchmark runs.
  Always set delete: true. Monitor sandbox lifetime via timeouts.
""")


def show_summary() -> None:
    """Display lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print("""
  Key Takeaways:
  1. Harbor supports 20+ environment providers beyond local Docker
  2. Cloud sandboxes turn CPU-bound evals into I/O-bound ones
  3. Use -e <provider> to select a cloud provider on the CLI
  4. Job configs specify provider via environment.type
  5. Provider-specific options go in environment.kwargs
  6. Always set delete: true to clean up cloud resources

  Generated configs: configs/docker-job.yaml, configs/daytona-job.yaml,
  configs/modal-job.yaml

  Next lesson: lesson-2-parallel-evaluation (scaling concurrent trials)
""")


def main() -> None:
    """Run the cloud-environments lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 3, Module 9          #")
    print("#          Lesson 1: Cloud Sandbox Environments         #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    list_environment_types()
    explain_cloud_vs_local()
    generate_job_configs()
    explain_environment_kwargs()
    show_cli_syntax()
    discuss_cost_and_setup()
    show_summary()


if __name__ == "__main__":
    main()
