"""
Explanatory output functions for the Configuration Sweeps lesson.

Extracted from main.py to keep it under 200 lines.
"""

from pathlib import Path


def explain_sweeps() -> None:
    """Explain what configuration sweeps are and why they matter."""
    print("=" * 60)
    print("Step 1: What Are Configuration Sweeps?")
    print("=" * 60)
    print()
    print("Configuration sweeps provide systematic, iterative exploration of")
    print("agent/model/config combinations across a set of tasks.")
    print()
    print("The key idea: each sweep round runs all remaining tasks. Tasks")
    print("that succeed (reward > 0) are DROPPED from future rounds. This")
    print("focuses compute on the hardest problems that still need solving.")
    print()
    print("Sweep strategy:")
    print("  Round 1: Run ALL tasks in the dataset")
    print("  -> Tasks with reward > 0 are removed from the pool")
    print("  Round 2: Run only REMAINING (failed) tasks")
    print("  -> Again, successful tasks are removed")
    print("  Round 3: Run only the stubborn failures")
    print("  -> Continue until max sweeps reached or all tasks pass")
    print()
    print("This is useful when:")
    print("  - You have a large benchmark and want to maximize coverage")
    print("  - Some tasks are flaky and may pass on retry")
    print("  - You want to combine sweeps with hints to help on hard tasks")
    print()


def show_sweep_config(config_path: Path, tasks_dir: Path) -> None:
    """Display and explain the sweep configuration file."""
    print("=" * 60)
    print("Step 2: Sweep Configuration")
    print("=" * 60)
    print()
    print(f"Sweep config file: {config_path}")
    print()
    config_text = config_path.read_text()
    print("--- sweep-config.yaml ---")
    for line in config_text.strip().splitlines():
        print(f"  {line}")
    print("--- end ---")
    print()
    print("This is a standard Harbor JobConfig YAML. The sweep command adds")
    print("extra behavior on top: iterative rounds and task filtering.")
    print()
    print("Our dataset has 3 tasks of increasing difficulty:")
    for task_dir in sorted(tasks_dir.iterdir()):
        if task_dir.is_dir():
            toml_path = task_dir / "task.toml"
            if toml_path.exists():
                content = toml_path.read_text()
                difficulty = "unknown"
                for line in content.splitlines():
                    if line.strip().startswith("difficulty"):
                        difficulty = line.split("=")[1].strip().strip('"')
                print(f"  - {task_dir.name} (difficulty: {difficulty})")
    print()


def explain_cli_flags() -> None:
    """Explain the harbor sweeps run command and its flags."""
    print("=" * 60)
    print("Step 3: The `harbor sweeps run` Command")
    print("=" * 60)
    print()
    print("Usage:")
    print("  harbor sweeps run -c <CONFIG> [OPTIONS]")
    print()
    print("Required:")
    print("  -c, --config <PATH>      Job config file (YAML or JSON)")
    print()
    print("Options:")
    print("  --max-sweeps <INT>       Max number of sweep rounds (default: 3)")
    print("  --trials-per-task <INT>  Trials per task per sweep (default: 2)")
    print("  --hint <STR>             Generic hint passed to all agents")
    print("  --hints-file <PATH>      JSON file mapping task names to hints")
    print("  --export-repo <STR>      HF repo for success/failure DatasetDict")
    print("  --push / --no-push       Push exported datasets to HF Hub")
    print()
    print("How it works internally:")
    print("  1. Load the JobConfig from --config")
    print("  2. Set n_attempts = --trials-per-task")
    print("  3. For each sweep round (up to --max-sweeps):")
    print("     a. Run a job with all remaining tasks")
    print("     b. Check result.json for each trial")
    print("     c. Tasks with any reward > 0 are dropped")
    print("  4. Stop when all tasks pass or max sweeps reached")
    print()


def explain_hints() -> None:
    """Explain how the hint system works with sweeps."""
    print("=" * 60)
    print("Step 6: Using Hints to Guide Agents")
    print("=" * 60)
    print()
    print("Sweeps support two hint mechanisms to help agents on hard tasks:")
    print()
    print("1. Generic hint (--hint):")
    print('   harbor sweeps run -c config.yaml --hint "Focus on edge cases"')
    print("   -> The hint string is added to every agent's kwargs as")
    print('      {"hint": "Focus on edge cases"}')
    print("   -> Useful when all tasks share a common strategy")
    print()
    print("2. Per-task hints (--hints-file):")
    print("   harbor sweeps run -c config.yaml --hints-file hints.json")
    print()
    print("   Example hints.json:")
    print("   {")
    print('     "tutorial/sweeps-reverse-string": "Use Python slicing [::-1]",')
    print('     "tutorial/sweeps-fibonacci": "Start with a=0, b=1",')
    print('     "tutorial/sweeps-json-transform": "Use json.load and sorted()"')
    print("   }")
    print()
    print("   When --hints-file is provided, each task gets its own")
    print("   individual job with a task-specific hint injected into the")
    print("   agent kwargs. This lets you give targeted guidance for the")
    print("   hardest tasks without wasting tokens on easy ones.")
    print()
    print("Hints are especially powerful in multi-round sweeps:")
    print("  Round 1: Run without hints -> easy tasks pass")
    print("  Round 2: Add hints for remaining hard tasks -> more pass")
    print("  Round 3: Stronger hints for the stubbornest failures")
    print()


def print_recap() -> None:
    """Print a summary of what was covered."""
    print("=" * 60)
    print("Recap")
    print("=" * 60)
    print()
    print("In this lesson you learned:")
    print()
    print("  1. SWEEPS are iterative evaluation rounds that drop successful")
    print("     tasks after each round, focusing compute on failures.")
    print()
    print("  2. The `harbor sweeps run` command takes a standard JobConfig")
    print("     and adds --max-sweeps, --trials-per-task, and hint flags.")
    print()
    print("  3. After each round, tasks with any reward > 0 are removed")
    print("     from the pool, so subsequent rounds only run hard tasks.")
    print()
    print("  4. HINTS (--hint for generic, --hints-file for per-task) let")
    print("     you guide agents on difficult tasks across sweep rounds.")
    print()
    print("  5. Sweeps are ideal for maximizing benchmark coverage when")
    print("     some tasks are flaky or benefit from retry/guidance.")
    print()
    print("Next lesson: analyze-check")
    print("  -> Use `harbor analyze` and `harbor check` to validate task")
    print("     quality with LLM-powered analysis.")
    print()
