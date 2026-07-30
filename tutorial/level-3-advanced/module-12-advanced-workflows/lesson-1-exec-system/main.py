"""
Harbor Tutorial — Module 12, Lesson 1: Exec Pipelines (Compile/Map/Reduce)

Demonstrates `harbor exec`, an experimental feature that compiles file paths
into Harbor tasks and runs an agent against each one.  The pipeline has three
phases: Compile, Map, and (optionally) Reduce.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

LESSON_DIR = Path(__file__).resolve().parent
SAMPLE_CODE_DIR = LESSON_DIR / "sample-code"
EXEC_CONFIG = LESSON_DIR / "exec-config.yaml"


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
            capture_output=True, text=True, timeout=10,
            check=False,
        )
        if result.returncode == 0:
            print(f"Harbor version: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    print("WARNING: 'harbor' CLI not found. Install with: uv tool install harbor")
    return False


def show_exec_config() -> None:
    """Display and explain the exec configuration file."""
    print_header("Step 1: The Exec Configuration File")
    print("Harbor exec uses a YAML config (ExecConfig) with two sections:")
    print("  - map:    compile rules + job config (required)")
    print("  - reduce: aggregation task + job config (optional)")
    print()
    print("--- exec-config.yaml ---")
    with open(EXEC_CONFIG) as f:
        print(f.read())
    print("--- end ---")
    print()
    print("The Compiler produces the Cartesian product of instructions x")
    print("environments, generating one task per combination.")


def show_cli_usage() -> None:
    """Show the various ways to invoke harbor exec."""
    print_header("Step 2: CLI Usage")
    commands = [
        ("From a config file", "harbor exec -c exec-config.yaml"),
        ("Inline paths + instruction", 'harbor exec -p "src/*.py" -i "Fix all bugs"'),
        ("Scan a directory", 'harbor exec -p src/ --scan -i "Review and improve"'),
        ("With agent and model", 'harbor exec -p "src/*.py" -a claude-code -m "anthropic/claude-sonnet-4-5-20250929" -i "Fix bugs"'),
        ("Print resolved config only", "harbor exec -c exec-config.yaml --print-config"),
        ("With artifact collection", 'harbor exec -p "src/*.py" -i "Fix bugs" -f result.py'),
    ]
    for desc, cmd in commands:
        print(f"  # {desc}")
        print(f"  {cmd}")
        print()
    print("Key flag groups:")
    print("  Compilation: -p/--path, --scan, -i/--instruction, --image, -f/--artifact")
    print("  Map Job:     -a/--agent, -m/--model, -n/--n-concurrent, -k/--n-attempts")
    print("  Reduce:      --ri/--reduce-instruction, --reduce-agent, --reduce-model")
    print("  Config:      -c/--config, --print-config")
    print()
    print("NOTE: `harbor exec` is experimental and may change in future releases.")


def explain_pipeline() -> None:
    """Explain the three-phase compile/map/reduce pipeline."""
    print_header("Step 3: The Compile / Map / Reduce Pipeline")
    print("The Executor class orchestrates three phases:")
    print()
    print("  Phase 1 -- COMPILE (Compiler class)")
    print("    Input:  instructions x environments (Cartesian product)")
    print("    Output: Harbor task directories on disk")
    print("    Action: Copy template, write instruction, write environment,")
    print("            generate auto-verifier, write task config TOML")
    print()
    print("  Phase 2 -- MAP (Job.create + job.run)")
    print("    Input:  compiled task directories + agent config")
    print("    Output: per-task trial results with rewards and artifacts")
    print("    Action: Create a Harbor Job, run agent on each task in parallel")
    print()
    print("  Phase 3 -- REDUCE (optional)")
    print("    Input:  map trial artifacts staged into numbered directories")
    print("    Output: a single aggregated result")
    print("    Action: Stage artifacts (0001-trial-name/, 0002-...), compile")
    print("            a reduce task, run a reduce agent on the aggregation")


def show_sample_files() -> None:
    """Display the sample Python files that would be compiled into tasks."""
    print_header("Step 4: Sample Files to Evaluate")
    py_files = sorted(SAMPLE_CODE_DIR.glob("*.py"))
    if not py_files:
        print("No sample files found!")
        return
    print(f"Found {len(py_files)} Python file(s) in {SAMPLE_CODE_DIR.name}/:")
    print()
    for filepath in py_files:
        rel = filepath.relative_to(LESSON_DIR)
        lines = filepath.read_text().strip().split("\n")
        docstring = lines[0] if lines else ""
        print(f"  {rel}: {docstring}  ({len(lines)} lines)")
    print()
    print("Each file would become a separate Harbor task.")


def simulate_compile_phase() -> None:
    """Simulate what the compile phase would produce."""
    print_header("Step 5: Simulating the Compile Phase")
    with open(EXEC_CONFIG) as f:
        config = yaml.safe_load(f) or {}
    if not isinstance(config, dict):
        raise TypeError(f"{EXEC_CONFIG} must have a mapping at the top level")

    compile_cfg = config.get("map", {}).get("compile", {})
    environments = compile_cfg.get("environments", [])
    instructions = compile_cfg.get("instructions", [])

    all_patterns: list[str] = []
    for env in environments:
        all_patterns.extend(env.get("paths", []))

    compiled_files: list[Path] = []
    for pattern in all_patterns:
        compiled_files.extend(sorted(LESSON_DIR.glob(pattern)))

    print(f"Input patterns: {all_patterns}")
    print(f"Compiled {len(compiled_files)} file(s):")
    for f in compiled_files:
        print(f"  {f.relative_to(LESSON_DIR)}  ({f.stat().st_size} bytes)")

    total = len(compiled_files) * len(instructions)
    print(f"\nCartesian product: {len(compiled_files)} files x "
          f"{len(instructions)} instruction(s) = {total} task(s)")


def show_use_cases() -> None:
    """Show common use cases for harbor exec."""
    print_header("Step 6: Common Use Cases")
    cases = [
        ("Code Review at Scale", 'harbor exec -p "src/**/*.py" --scan -i "Review for bugs"'),
        ("API Migration", 'harbor exec -p "legacy/*.py" -i "Migrate from v1 to v2 API"'),
        ("Documentation", 'harbor exec -p "lib/*.py" -i "Add comprehensive docstrings"'),
        ("Test Generation", 'harbor exec -p "src/*.py" -i "Write unit tests"'),
    ]
    for title, cmd in cases:
        print(f"  {title}:")
        print(f"    {cmd}")
        print()
    print("The exec system turns any collection of files into a")
    print("structured evaluation -- no manual task scaffolding required.")


def main() -> None:
    print_header("Harbor Exec Pipelines (Compile / Map / Reduce)")
    print("This lesson explores `harbor exec`, an experimental feature")
    print("that compiles file paths into Harbor tasks and evaluates them.")
    print()
    check_harbor_installed()
    show_exec_config()
    show_cli_usage()
    explain_pipeline()
    show_sample_files()
    simulate_compile_phase()
    show_use_cases()

    print_header("Summary")
    print("harbor exec automates the creation of tasks from source files:")
    print("  1. COMPILE: paths/globs  -->  individual files")
    print("  2. MAP:     files        -->  Harbor tasks + agent runs")
    print("  3. REDUCE:  trial results --> aggregated report (optional)")
    print()
    print("NOTE: harbor exec is experimental and may change in future releases.")


if __name__ == "__main__":
    main()
