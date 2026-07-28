"""
Lesson 1: What Are Adapters?

Adapters convert external benchmarks (SWE-bench, HumanEval, MBPP, etc.)
into Harbor's standard task format so any agent can be evaluated against them.
"""

import shutil
import subprocess
import sys


# ── A curated selection of the 85+ adapters available in Harbor ──────────
ADAPTER_CATALOG: dict[str, list[str]] = {
    "Software Engineering": [
        "swebench         — Real GitHub issues from popular Python repos (500 tasks)",
        "swebenchpro       — Harder SWE-bench subset, professional-grade issues",
        "multi-swe-bench   — Multi-language SWE-bench (Java, JS, Go, Rust, C++)",
        "swesmith          — Synthetically generated SWE-bench-style tasks",
    ],
    "Code Generation & Repair": [
        "humanevalfix      — Code repair from HumanEvalPack (164 tasks)",
        "bigcodebench_hard — Hard code generation from BigCodeBench",
        "livecodebench     — Continuously updated competitive programming",
        "compilebench      — Compile-and-fix tasks across languages",
    ],
    "Data & SQL": [
        "bird_bench        — Text-to-SQL over real databases",
        "spider2-dbt       — Advanced SQL/dbt data transformation tasks",
        "ds1000            — Data science coding (NumPy, Pandas, etc.)",
    ],
    "Science, Math & Security": [
        "gpqa-diamond      — Graduate-level science Q&A (PhD-difficulty)",
        "scicode           — Scientific computing and simulation",
        "omnimath          — Olympiad-level math problems",
        "cybergym          — Cybersecurity CTF challenges",
    ],
    "General Reasoning": [
        "gaia / gaia2      — General AI Assistant benchmark",
        "hle               — Humanity's Last Exam — expert-level questions",
        "simpleqa          — Simple factual Q&A for calibration",
    ],
}


def show_intro() -> None:
    """Explain what adapters are and why they exist."""
    print("=" * 60)
    print("What Are Adapters?")
    print("=" * 60)
    print()
    print("Harbor evaluates agents by running them against tasks inside")
    print("containers. But the AI ecosystem already has dozens of popular")
    print("benchmarks — SWE-bench, HumanEval, GAIA, BIRD, and many more.")
    print()
    print("Adapters bridge this gap. An adapter takes an external")
    print("benchmark's native format and converts it into Harbor's")
    print("standard task directory structure:")
    print()
    print("  External Benchmark   -->   Adapter   -->   Harbor Tasks")
    print("  (HuggingFace, GitHub)       (Python)        (task dirs)")
    print()
    print("This means:")
    print("  - Any agent can run against any benchmark")
    print("  - Results are comparable across agents and benchmarks")
    print("  - New benchmarks only need one adapter, not per-agent work")
    print()


def show_adapter_catalog() -> None:
    """List major adapters available in Harbor."""
    print("=" * 60)
    print("Available Adapters (85+ in Harbor)")
    print("=" * 60)
    print()
    for category, items in ADAPTER_CATALOG.items():
        print(f"  {category}:")
        for item in items:
            print(f"    {item}")
        print()
    print("  ... and 60+ more covering ML, finance, web, agents, etc.")
    print()


def show_adapter_structure() -> None:
    """Show the standard directory structure of a Harbor adapter."""
    print("=" * 60)
    print("Adapter Directory Structure")
    print("=" * 60)
    print()
    print("  adapters/my-adapter/")
    print("  ├── adapter_metadata.json   # Benchmark info, parity data")
    print("  ├── pyproject.toml          # Python package definition")
    print("  ├── my_adapter.yaml         # Default job configuration")
    print("  └── src/my_adapter/")
    print("      ├── adapter.py          # Core conversion logic")
    print("      ├── main.py             # CLI entry point")
    print("      └── task-template/      # Template files for tasks")
    print("          ├── instruction.md")
    print("          ├── task.toml")
    print("          ├── environment/Dockerfile")
    print("          ├── tests/test.sh")
    print("          └── solution/solve.sh")
    print()


def show_pipeline() -> None:
    """Show the conversion pipeline with an ASCII diagram."""
    print("=" * 60)
    print("The Adapter Pipeline")
    print("=" * 60)
    print()
    print("  ┌────────────────────────────────────────────────────┐")
    print("  │               ADAPTER PIPELINE                     │")
    print("  │                                                    │")
    print("  │  1. FETCH   — Download from HuggingFace / GitHub   │")
    print("  │       │                                            │")
    print("  │       v                                            │")
    print("  │  2. PARSE   — Read each instance: problem, tests,  │")
    print("  │       │       repo snapshots, expected outputs     │")
    print("  │       v                                            │")
    print("  │  3. CONVERT — Generate Harbor task files:           │")
    print("  │       │       instruction.md, task.toml, Dockerfile│")
    print("  │       │       test.sh, solve.sh                    │")
    print("  │       v                                            │")
    print("  │  4. OUTPUT  — Write to datasets/<name>/            │")
    print("  │              Ready for: harbor run -p <path> -a ..│")
    print("  └────────────────────────────────────────────────────┘")
    print()


def show_usage() -> None:
    """Show how to use an adapter."""
    print("=" * 60)
    print("Using an Adapter")
    print("=" * 60)
    print()
    print("Option A: Pre-built registered dataset (easiest)")
    print("  $ harbor dataset list")
    print("  $ harbor run -d harbor-framework/swe-bench-verified-mini \\")
    print("               -a claude-code -m anthropic/claude-sonnet-4-5-20250929")
    print()
    print("Option B: Run the adapter yourself (full control)")
    print("  $ cd adapters/swebench && uv sync")
    print("  $ uv run swebench          # generates task dirs")
    print("  $ harbor run -c swebench.yaml")
    print()


def try_list_datasets() -> None:
    """Try to list registered datasets if Harbor is installed."""
    print("=" * 60)
    print("Registered Datasets")
    print("=" * 60)
    print()
    if not shutil.which("harbor"):
        print("  Harbor CLI not found. Install: uv tool install harbor")
        print()
        return
    result = subprocess.run(
        ["harbor", "dataset", "list"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode == 0 and result.stdout.strip():
        for line in result.stdout.strip().split("\n")[:15]:
            print(f"  {line}")
        total = len(result.stdout.strip().split("\n"))
        if total > 15:
            print(f"  ... and {total - 15} more")
    else:
        print("  Could not list datasets (Harbor may need configuration).")
    print()


def show_summary() -> None:
    """Display a summary of what was learned."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("Key takeaways:")
    print("  1. Adapters convert external benchmarks into Harbor tasks")
    print("  2. Harbor ships with 85+ adapters (SE, math, security, ...)")
    print("  3. Standard structure: adapter_metadata.json, adapter.py,")
    print("     task-template/")
    print("  4. Pipeline: Fetch -> Parse -> Convert -> Output")
    print("  5. Use pre-built datasets or run adapters yourself")
    print()
    print("Next lesson: lesson-2-swe-bench-adapter")
    print("  (Running SWE-Bench — the most popular SE benchmark)")


def main() -> None:
    """Run the adapter-intro lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 3, Module 9          #")
    print("#          Lesson 1: What Are Adapters?                 #")
    print("########################################################")
    print()

    show_intro()
    show_adapter_catalog()
    show_adapter_structure()
    show_pipeline()
    show_usage()
    try_list_datasets()
    show_summary()


if __name__ == "__main__":
    main()
