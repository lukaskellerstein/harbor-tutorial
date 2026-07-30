"""
Lesson 2: Parallel Evaluation

Learn how to run multiple trials concurrently to speed up
large-scale evaluations. Compare serial vs parallel execution
using local Docker with the oracle agent.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from helpers import generate_configs, run_evaluation


def check_prerequisites() -> bool:
    """Verify Harbor CLI and Docker are available."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
    print("=" * 60)

    if not shutil.which("harbor"):
        print("  [FAIL] Harbor CLI not found. Install with: uv tool install harbor")
        return False
    print("  [OK] Harbor CLI is installed")

    result = subprocess.run(
        ["docker", "info"], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        print("  [FAIL] Docker daemon is not running. Start Docker Desktop.")
        return False
    print("  [OK] Docker is running")
    print()
    return True


def explain_parallelism() -> None:
    """Explain why parallelism matters for evaluation."""
    print("=" * 60)
    print("Step 2: Why Parallelism Matters")
    print("=" * 60)
    print("""
  Each trial involves building a container, running the agent, and
  verifying results. A single trial might take 1-10 minutes.

    Sequential (n=1):   500 tasks x 5 min = ~42 hours
    Parallel   (n=4):   500 tasks x 5 min / 4 = ~10.5 hours
    Parallel   (n=32):  500 tasks x 5 min / 32 = ~1.3 hours (cloud)

  The -n flag (or n_concurrent_trials) controls concurrency.
""")


def show_concurrency_config() -> None:
    """Show how to configure concurrency."""
    print("=" * 60)
    print("Step 3: Configuring Concurrency")
    print("=" * 60)
    print("""
  CLI flag:
    harbor run -d <dataset> -a <agent> -n 4

  Job config (top-level field):
    n_concurrent_trials: 4
    quiet: false

  NOTE: The 'orchestrator' config key is deprecated. Use top-level
  'n_concurrent_trials' and 'quiet' instead.

  Per-agent sub-limits:
    agents:
      - name: claude-code
        n_concurrent: 2       # Per-agent cap under global limit
""")


def show_task_dataset() -> None:
    """Display the 4-task dataset structure."""
    print("=" * 60)
    print("Step 4: Dataset with 4 Simple Tasks")
    print("=" * 60)

    tasks_dir = Path(__file__).parent / "tasks"
    print(f"\n  Dataset directory: {tasks_dir}\n")

    for i in range(1, 5):
        instruction = tasks_dir / f"task-{i}" / "instruction.md"
        if instruction.exists():
            content = instruction.read_text().strip()
            print(f"  task-{i}/ : {content[:60]}...")
    print()


def do_generate_configs() -> None:
    """Generate serial and parallel job configs."""
    print("=" * 60)
    print("Step 5: Generating Job Configs")
    print("=" * 60)

    configs_dir = Path(__file__).parent / "configs"
    tasks_dir = Path(__file__).parent / "tasks"
    generate_configs(configs_dir, tasks_dir)


def run_comparison() -> None:
    """Run serial vs parallel evaluation and compare times."""
    print("=" * 60)
    print("Step 6: Serial vs Parallel -- Timing Comparison")
    print("=" * 60)

    print("\n  Running 4 tasks with the oracle agent...")
    print("  First serial (n=1), then parallel (n=4).\n")

    configs_dir = Path(__file__).parent / "configs"
    cwd = Path(__file__).parent

    serial_time = run_evaluation(
        configs_dir / "serial.yaml", "Serial (n_concurrent_trials=1)", cwd
    )
    print()
    parallel_time = run_evaluation(
        configs_dir / "parallel.yaml", "Parallel (n_concurrent_trials=4)", cwd
    )

    print()
    print("=" * 60)
    print("Step 7: Results Comparison")
    print("=" * 60)
    print(f"\n  Serial   (n=1): {serial_time:6.1f} seconds")
    print(f"  Parallel (n=4): {parallel_time:6.1f} seconds\n")

    if parallel_time > 0 and serial_time > parallel_time:
        speedup = serial_time / parallel_time
        print(f"  Speedup: {speedup:.1f}x faster with parallel execution")
    else:
        print("  Note: With small/fast tasks, parallelism overhead may")
        print("  reduce the speedup. The benefit grows with longer tasks.")

    print("""
  With cloud environments, this gets even better:
    - Cloud sandboxes make trials I/O-bound (not CPU-bound)
    - Scale to 32, 64, or 128+ concurrent trials
    - Example: harbor run -d <dataset> -a claude-code -e daytona -n 32
""")


def show_summary() -> None:
    """Display lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print("""
  Key Takeaways:
  1. Use -n <N> or n_concurrent_trials to set concurrency
  2. The 'orchestrator' config key is deprecated; use top-level fields
  3. Per-agent n_concurrent provides sub-limits within the global cap
  4. Local Docker: CPU-bound (typically 2-8 concurrent)
  5. Cloud sandboxes: I/O-bound (32-128+ concurrent)
  6. Speedup is most dramatic with longer-running tasks

  Next lesson: lesson-3-network-policies (controlling network access)
""")


def main() -> None:
    """Run the parallel-evaluation lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 3, Module 10         #")
    print("#          Lesson 2: Parallel Evaluation                #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_parallelism()
    show_concurrency_config()
    show_task_dataset()
    do_generate_configs()
    run_comparison()
    show_summary()


if __name__ == "__main__":
    main()
