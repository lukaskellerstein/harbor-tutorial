"""
Lesson 2: Running SWE-Bench with Harbor

SWE-bench is the most widely used benchmark for evaluating AI agents
on real-world software engineering tasks. This lesson explains how
Harbor's SWE-bench adapter works and how to run evaluations.

NOTE: Running SWE-bench is expensive and slow. This lesson is designed
as "read and understand" with an optional run at the end.
"""

import shutil
import subprocess
from pathlib import Path


def check_prerequisites() -> bool:
    """Check that Harbor and Docker are available."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
    print("=" * 60)
    print()
    harbor_ok = bool(shutil.which("harbor"))
    docker_ok = False
    if harbor_ok:
        print("  [OK] Harbor CLI is installed")
    else:
        print("  [WARN] Harbor CLI not found (install: uv tool install harbor)")
    if shutil.which("docker"):
        result = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, check=False
        )
        docker_ok = result.returncode == 0
    print(f"  [{'OK' if docker_ok else 'WARN'}] Docker is {'running' if docker_ok else 'not running'}")
    print()
    return harbor_ok and docker_ok


def explain_swe_bench() -> None:
    """Explain what SWE-bench is and why it matters."""
    print("=" * 60)
    print("Step 2: What Is SWE-Bench?")
    print("=" * 60)
    print()
    print("SWE-bench evaluates AI agents on real GitHub issues from")
    print("popular open-source Python projects (Django, Flask, sympy,")
    print("scikit-learn, matplotlib, requests, pytest, and more).")
    print()
    print("Each instance consists of:")
    print("  - A real GitHub issue (bug report or feature request)")
    print("  - The repository at the commit before the fix")
    print("  - The original developer's patch (ground truth)")
    print("  - The test suite that validates the fix")
    print()
    print("SWE-bench Verified: 500 human-validated instances chosen")
    print("for clear problem statements and reliable tests.")
    print()


def show_adapter_flow() -> None:
    """Show how the SWE-bench adapter converts instances to tasks."""
    print("=" * 60)
    print("Step 3: How the SWE-Bench Adapter Works")
    print("=" * 60)
    print()
    print("  HuggingFace Field            Harbor Task File")
    print("  ─────────────────            ────────────────")
    print("  problem_statement     -->    instruction.md")
    print("  repo + base_commit    -->    Dockerfile (repo checkout)")
    print("  test_patch            -->    test.sh (apply + run tests)")
    print("  patch (ground truth)  -->    solve.sh (reference fix)")
    print("  instance metadata     -->    task.toml (config)")
    print()
    print("The Dockerfile checks out the repo at the base commit and")
    print("installs dependencies. The test script applies the test")
    print("patch and writes reward (1.0/0.0) to /logs/verifier/reward.txt.")
    print()


def show_job_config() -> None:
    """Show and explain the SWE-bench job configuration."""
    print("=" * 60)
    print("Step 4: SWE-Bench Job Configuration")
    print("=" * 60)
    print()
    job_file = Path(__file__).parent / "swe-bench-job.yaml"
    if job_file.exists():
        print(f"File: {job_file.name}")
        print()
        print(job_file.read_text())
    print("Key settings:")
    print("  n_attempts: 1         — attempts per task (increase for stats)")
    print("  n_concurrent_trials: 1 — parallel trials (limited by resources)")
    print("  force_build: true     — rebuild Docker images each time")
    print("  delete: true          — remove containers after trial")
    print("  dataset: swe-bench-verified-mini — small subset for testing")
    print()


def show_cli_commands() -> None:
    """Show the CLI commands for running SWE-bench."""
    print("=" * 60)
    print("Step 5: Running SWE-Bench")
    print("=" * 60)
    print()
    print("From job config:")
    print("  $ harbor run -c swe-bench-job.yaml")
    print()
    print("Single instance for testing:")
    print("  $ harbor run -d harbor-framework/swe-bench-verified-mini \\")
    print("               -a claude-code \\")
    print("               -m anthropic/claude-sonnet-4-5-20250929 -n 1")
    print()
    print("With cloud environment for parallelism:")
    print("  $ harbor run -d harbor-framework/swe-bench-verified \\")
    print("               -a claude-code -e daytona -n 32 \\")
    print("               -m anthropic/claude-sonnet-4-5-20250929")
    print()


def show_cost_and_results() -> None:
    """Discuss cost considerations and results structure."""
    print("=" * 60)
    print("Step 6: Cost, Time, and Results")
    print("=" * 60)
    print()
    print("  Per Trial:  build 1-5 min, agent 2-30 min, cost $0.05-$2.00")
    print("  Full (500): sequential ~3-7 days, 8x parallel ~10-20 hours,")
    print("              32x parallel (cloud) ~3-5 hours, cost $25-$500+")
    print()
    print("  Tips: start with mini dataset, n_attempts=1, -n 1 first")
    print()
    print("Results are stored in jobs/<job-id>/trials/<instance-id>/:")
    print("  config.json    — trial configuration")
    print("  result.json    — reward, timing, status")
    print("  trajectory/    — agent execution trace")
    print("  verifier/      — test output and reward")
    print()
    print("View results: $ harbor view jobs")
    print()


def offer_optional_run(prerequisites_ok: bool) -> None:
    """Offer to run a minimal SWE-bench evaluation."""
    print("=" * 60)
    print("Step 7: Optional — Try It Yourself")
    print("=" * 60)
    print()
    if not prerequisites_ok:
        print("  Prerequisites not met. To try SWE-bench yourself:")
        print("  1. Install Harbor: uv tool install harbor")
        print("  2. Start Docker Desktop")
        print("  3. Set ANTHROPIC_API_KEY in your environment")
        print("  4. Run: harbor run -c swe-bench-job.yaml")
    else:
        print("  To run a single SWE-bench task (costs ~$0.10-$2.00):")
        print("  $ harbor run -c swe-bench-job.yaml")
        print()
        print("  This lesson does NOT auto-run SWE-bench to avoid")
        print("  unexpected costs. Run the command above manually.")
    print()


def show_summary() -> None:
    """Display a summary of what was learned."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("Key takeaways:")
    print("  1. SWE-bench evaluates agents on real GitHub issues")
    print("  2. The adapter converts HuggingFace instances into Harbor")
    print("     tasks (instruction, Dockerfile, tests, solution)")
    print("  3. Configure runs with a job.yaml file")
    print("  4. Start small (mini dataset, -n 1) before scaling")
    print("  5. Full runs are expensive — plan your budget")
    print()
    print("Next lesson: lesson-3-swe-bench-claude-code")
    print("  (End-to-end SWE-bench evaluation with the claude-code agent)")


def main() -> None:
    """Run the swe-bench-adapter lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 3, Module 9          #")
    print("#          Lesson 2: Running SWE-Bench                  #")
    print("########################################################")
    print()

    prerequisites_ok = check_prerequisites()
    explain_swe_bench()
    show_adapter_flow()
    show_job_config()
    show_cli_commands()
    show_cost_and_results()
    offer_optional_run(prerequisites_ok)
    show_summary()


if __name__ == "__main__":
    main()
