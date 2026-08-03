"""
Lesson: Benchmarking Claude Code on SWE-bench

End-to-end walkthrough: configure, run, and analyze a SWE-bench
evaluation using Harbor's built-in claude-code agent.

This lesson actually runs the benchmark (on the mini subset by default).
Requires ANTHROPIC_API_KEY and Docker.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from results import find_latest_job, load_trial_results, print_results_table

LESSON_DIR = Path(__file__).parent
JOBS_DIR = LESSON_DIR / "jobs"


def check_prerequisites() -> bool:
    """Verify Docker, Harbor, and ANTHROPIC_API_KEY."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
    print("=" * 60)
    print()

    ok = True
    if shutil.which("docker"):
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            print("  [OK] Docker is running")
        else:
            print("  [FAIL] Docker daemon is not running")
            ok = False
    else:
        print("  [FAIL] Docker not found")
        ok = False

    if shutil.which("harbor"):
        print("  [OK] Harbor CLI installed")
    else:
        print("  [FAIL] Harbor CLI not found (uv tool install harbor)")
        ok = False

    if os.environ.get("ANTHROPIC_API_KEY"):
        print("  [OK] ANTHROPIC_API_KEY is set")
    else:
        print("  [FAIL] ANTHROPIC_API_KEY not set")
        print("         export ANTHROPIC_API_KEY=sk-ant-...")
        ok = False

    print()
    return ok


def explain_benchmark() -> None:
    """Explain what we're about to do and why."""
    print("=" * 60)
    print("Step 2: What We're Running")
    print("=" * 60)
    print()
    print("  Benchmark : SWE-bench Verified (mini subset)")
    print("  Agent     : claude-code (built-in Harbor agent)")
    print("  Model     : anthropic/claude-sonnet-4-5-20250929")
    print("  Env       : Docker (local)")
    print()
    print("  Each SWE-bench task checks out a real repo, gives the agent")
    print("  the issue description, and runs the project's test suite to")
    print("  verify the fix. Cost per task: ~$0.10-$2.00, time: 2-15 min.")
    print()


def show_job_configs() -> None:
    """Show the three job configs and explain the differences."""
    print("=" * 60)
    print("Step 3: Job Configurations (3 scales)")
    print("=" * 60)
    print()

    configs = [
        ("swe-bench-job.yaml", "Mini subset, local, sequential (~$1-5)"),
        ("swe-bench-full.yaml", "Full 500, local, 8 parallel (~$50-500)"),
        ("swe-bench-cloud.yaml", "Full 500, Daytona, 32 parallel (~3-5h)"),
    ]
    for filename, description in configs:
        path = LESSON_DIR / filename
        print(f"  {filename} — {description}")
        if path.exists():
            for line in path.read_text().strip().split("\n"):
                print(f"    {line}")
        print()


def run_benchmark() -> bool:
    """Run SWE-bench mini with Claude Code."""
    print("=" * 60)
    print("Step 4: Running the Benchmark")
    print("=" * 60)
    print()
    print("  Running: harbor run -c swe-bench-job.yaml")
    print("  (downloads dataset, builds containers, runs agent, verifies)")
    print()
    print("-" * 60)

    result = subprocess.run(
        ["harbor", "run", "-c", "swe-bench-job.yaml"],
        capture_output=False,
        text=True,
        cwd=str(LESSON_DIR),
        check=False,
    )

    print("-" * 60)
    print()
    success = result.returncode == 0
    if success:
        print("  Benchmark completed successfully!")
    else:
        print(f"  Benchmark exited with code {result.returncode}")
        print("  Check the output above for errors.")
    print()
    return success


def analyze_results() -> None:
    """Parse and display benchmark results."""
    print("=" * 60)
    print("Step 5: Analyzing Results")
    print("=" * 60)
    print()

    job_dir = find_latest_job(JOBS_DIR)
    if not job_dir:
        print("  No results found. Run: harbor run -c swe-bench-job.yaml")
        return

    print(f"  Job: {job_dir.name}")
    print()

    results = load_trial_results(job_dir)
    if not results:
        print("  No trial results found yet.")
        return

    print_results_table(results)
    print()


def show_next_steps() -> None:
    """Show commands for deeper inspection and scaling."""
    print("=" * 60)
    print("Step 6: Next Steps")
    print("=" * 60)
    print()
    print("  Browse results  : harbor view jobs")
    print("  Analyze behavior: harbor analyze jobs/<job-id>")
    print("  Scale up (local) : harbor run -c swe-bench-full.yaml")
    print("  Scale up (cloud) : harbor run -c swe-bench-cloud.yaml")
    print()
    print("  Compare agents by editing the 'agents' section in job.yaml:")
    print("    agents:")
    print("      - name: aider")
    print("        model_name: anthropic/claude-sonnet-4-5-20250929")
    print()


def show_summary() -> None:
    """Print key takeaways."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("  You just benchmarked Claude Code on real GitHub issues!")
    print()
    print("  Key takeaways:")
    print("  1. SWE-bench is the industry standard for coding agent eval")
    print("  2. Harbor + claude-code makes it a single command:")
    print("       harbor run -c swe-bench-job.yaml")
    print("  3. Start small (mini), then scale (full + cloud parallel)")
    print("  4. Compare agents by swapping the 'agents' section")
    print("  5. Use 'harbor view' and 'harbor analyze' for deeper insight")
    print()
    print("  Next lesson: lesson-4-custom-adapter")
    print("    (Build your own benchmark adapter from scratch)")


def main() -> None:
    """Run the SWE-bench Claude Code benchmark lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 3, Module 9          #")
    print("#  Benchmarking Claude Code on SWE-bench                #")
    print("########################################################")
    print()

    if not check_prerequisites():
        print("  Fix the prerequisites above and re-run.")
        sys.exit(1)

    explain_benchmark()
    show_job_configs()
    success = run_benchmark()
    if success:
        analyze_results()
    show_next_steps()
    show_summary()


if __name__ == "__main__":
    main()
