"""
Harbor Tutorial — Module 12, Lesson 3: Hub — Sharing & Leaderboards

Demonstrates Harbor Hub, the platform for sharing datasets, uploading
evaluation results, browsing community benchmarks, and viewing
leaderboards.  Hub features require authentication and network access,
so this lesson is informational.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

LESSON_DIR = Path(__file__).resolve().parent


def print_header(title: str) -> None:
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()


def check_harbor_installed() -> bool:
    """Check whether the harbor CLI is available."""
    try:
        result = subprocess.run(
            ["harbor", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            print(f"Harbor version: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    print("WARNING: 'harbor' CLI not found. Install: uv tool install harbor")
    return False


def explain_hub() -> None:
    """Introduce Harbor Hub and its purpose."""
    print_header("Step 1: What is Harbor Hub?")
    print("Harbor Hub (hub.harborframework.com) is the community platform")
    print("for the Harbor ecosystem. It serves three purposes:")
    print("  1. SHARING   -- Publish datasets for others to evaluate against")
    print("  2. COMPETING -- Upload results and see how your agent ranks")
    print("  3. BROWSING  -- Discover community benchmarks and datasets")


def show_authentication() -> None:
    """Explain Hub authentication."""
    print_header("Step 2: Authentication")
    print("Harbor uses GitHub OAuth (PKCE flow) for authentication.")
    print("Credentials are stored at ~/.harbor/credentials.json (0600).")
    print("API key format: sk-harbor-<key_id>_<secret>")
    print()
    print("  harbor auth login              # GitHub OAuth (opens browser)")
    print("  harbor auth login --no-browser # Headless environments")
    print("  harbor auth status             # Check auth mode (env/file/none)")
    print("  harbor auth logout             # Revoke key and delete creds")
    print("  harbor auth key list           # List your API keys")
    print("  harbor auth key revoke         # Revoke a specific key")
    print()
    print("Tip: Set HARBOR_API_KEY env var to bypass the login flow.")


def show_publishing() -> None:
    """Show how to publish datasets to the Hub."""
    print_header("Step 3: Publishing Datasets")
    print("`harbor publish` uploads task/dataset definitions to the registry.")
    print("It auto-detects tasks (task.toml) vs datasets (dataset.toml).")
    print()
    print("  harbor check -p path/to/dataset         # Validate first")
    print("  harbor publish path/to/dataset           # Publish (private)")
    print("  harbor publish path/to/dataset --public  # Publish publicly")
    print()
    print("Publishing workflow:")
    print("  1. Compute content hash of all task files")
    print("  2. Create tar.gz archive and upload to storage")
    print("  3. Register under your org namespace (org/dataset-name)")
    print()
    print("Options: --tag <name> (repeatable), --public/--private,")
    print("         --concurrency <n> (default: 50)")


def show_uploading() -> None:
    """Show how to upload evaluation results."""
    print_header("Step 4: Uploading Results")
    print("`harbor upload` uploads job results (not definitions) to Hub.")
    print()
    print("  harbor upload jobs/<job-id>                      # Upload results")
    print("  harbor upload jobs/<job-id> --public             # Public visibility")
    print("  harbor upload jobs/<job-id> --share-org my-team  # Share with org")
    print('  harbor run -d "org/dataset" -a agent --upload    # Auto-upload')
    print()
    print("Three-phase streaming process:")
    print("  1. start_job    -- insert job row into Hub database")
    print("  2. upload_trial -- per-trial: archive + trajectory upload")
    print("  3. finalize     -- job-level archive, mark as finished")
    print()
    print("The process is idempotent -- safe to re-run after crashes.")
    print("After upload: https://hub.harborframework.com/jobs/<job-id>")


def show_leaderboards() -> None:
    """Explain how leaderboards work."""
    print_header("Step 5: Leaderboards")
    print("Leaderboards rank agents/models on published datasets.")
    print()
    print("  Metric            Description")
    print("  ------            -----------")
    print("  Mean Reward       Average reward across tasks (0-1)")
    print("  Pass Rate         Percentage with reward = 1")
    print("  Median Duration   Typical time per task")
    print("  Cost              Estimated API cost per task")
    print()
    print("CLI commands (harbor hub leaderboard):")
    print("  list              List leaderboards")
    print("  show <ref>        View a leaderboard (UUID or org/pkg/name)")
    print("  init              Initialize from YAML config")
    print("  create            Create a new leaderboard")
    print("  export <ref>      Export as JSON/CSV")
    print("  row list <ref>    List rows")
    print("  row create ...    Add a row")


def show_browsing() -> None:
    """Show how to browse and download community datasets."""
    print_header("Step 6: Browsing & Downloading")
    print("  harbor dataset list                  # List registered datasets")
    print("  harbor download org/name             # Download dataset")
    print("  harbor download org/name@v1.0        # Specific version")
    print("  harbor download org/name -o ./dir    # Custom output dir")
    print("  harbor download org/name --cache     # Content-addressable cache")
    print()

    # Try to list datasets
    try:
        result = subprocess.run(
            ["harbor", "dataset", "list"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            print("Available datasets:")
            for line in lines[:10]:
                print(f"  {line}")
            if len(lines) > 10:
                print(f"  ... and {len(lines) - 10} more")
        else:
            print("  (Could not retrieve dataset list)")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("  (Harbor CLI not available for live listing)")

    print()
    print("Hub also provides job/trial browsing:")
    print("  harbor hub job list             # List your jobs")
    print("  harbor hub job show <id>         # Job details")
    print("  harbor hub job download <id>     # Download results")
    print("  harbor hub trial show <id>       # Trial details")


def show_workflow() -> None:
    """Show the complete Hub workflow."""
    print_header("Step 7: The Complete Hub Workflow")
    print("  CREATE  -->  TEST  -->  PUBLISH  -->  SHARE  -->  COMPETE")
    print()
    print("  1. CREATE  -- Build tasks (instruction, environment, tests)")
    print("  2. TEST    -- Run oracle agent to verify all tasks work")
    print("  3. PUBLISH -- harbor publish path/to/dataset")
    print("  4. SHARE   -- Others find via harbor dataset list")
    print("  5. COMPETE -- Run agents, upload results, climb leaderboard")
    print()
    print("Best practices:")
    print("  DO: Test with oracle, use harbor check, set appropriate timeouts")
    print("  AVOID: Flaky tests, embedded secrets, extremely long timeouts")


def main() -> None:
    print_header("Harbor Hub -- Sharing & Leaderboards")
    print("This lesson explores Harbor Hub, the community platform for")
    print("sharing datasets, uploading results, and viewing leaderboards.")
    print()
    print("NOTE: Hub features require authentication and network access.")
    print()
    check_harbor_installed()
    explain_hub()
    show_authentication()
    show_publishing()
    show_uploading()
    show_leaderboards()
    show_browsing()
    show_workflow()

    print_header("Summary")
    print("Harbor Hub connects the evaluation community:")
    print("  harbor auth login          Log in (GitHub OAuth)")
    print("  harbor publish <path>      Share a dataset")
    print("  harbor upload <job-path>   Upload results to leaderboard")
    print("  harbor dataset list        Browse available datasets")
    print("  harbor download <name>     Download a community dataset")
    print()
    print("This is the final lesson in Module 12 (Advanced Workflows).")


if __name__ == "__main__":
    main()
