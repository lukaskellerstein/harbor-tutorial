"""
Lesson 3: Building a Custom Adapter

Demonstrates how to build a custom adapter that converts a CSV file
of coding challenges into Harbor task directories. Shows the core
conversion logic that every adapter implements.
"""

import shutil
import subprocess
from pathlib import Path

from adapter import load_challenges, run_adapter


def explain_adapter_scaffolding() -> None:
    """Explain how to scaffold a new adapter with harbor adapter init."""
    print("=" * 60)
    print("Step 1: Scaffolding a New Adapter")
    print("=" * 60)
    print()
    print("Harbor provides an interactive wizard to scaffold adapters:")
    print()
    print("  $ harbor adapter init")
    print()
    print("The wizard asks for adapter name, benchmark source, task type,")
    print("and author info. It generates:")
    print()
    print("  adapters/my-benchmark/")
    print("  ├── adapter_metadata.json")
    print("  ├── pyproject.toml")
    print("  ├── my_benchmark.yaml")
    print("  └── src/my_benchmark/")
    print("      ├── adapter.py    # Fill in conversion logic here")
    print("      ├── main.py")
    print("      └── task-template/")
    print()
    print("Validate your adapter: $ harbor adapter review")
    print()
    print("In this lesson, we build the conversion logic directly.")
    print()


def show_source_data() -> None:
    """Show the CSV source data we will convert."""
    print("=" * 60)
    print("Step 2: The Source Data (challenges.csv)")
    print("=" * 60)
    print()

    csv_path = Path(__file__).parent / "challenges.csv"
    if not csv_path.exists():
        print("  ERROR: challenges.csv not found!")
        return

    print("  Columns: id, instruction, expected_output, difficulty")
    print()
    for i, ch in enumerate(load_challenges(csv_path), 1):
        instr = ch.instruction[:67] + "..." if len(ch.instruction) > 70 else ch.instruction
        print(f"  Challenge {i}: {ch.id} (difficulty: {ch.difficulty})")
        print(f"    Instruction: {instr}")
        print(f"    Expected:    output contains '{ch.expected_output}'")
        print()


def run_conversion() -> list[Path]:
    """Run the adapter to generate Harbor task directories."""
    print("=" * 60)
    print("Step 3: Running the Adapter")
    print("=" * 60)
    print()

    csv_path = Path(__file__).parent / "challenges.csv"
    output_dir = Path(__file__).parent / "generated-tasks"

    if output_dir.exists():
        shutil.rmtree(output_dir)

    print(f"Source:  {csv_path.name}")
    print(f"Output:  {output_dir.name}/")
    print()
    print("Converting challenges to Harbor tasks...")
    print()

    generated = run_adapter(csv_path, output_dir, dataset_name="coding-challenges")
    for task_dir in generated:
        print(f"  Generated: {task_dir.name}/")

    print(f"\nTotal tasks generated: {len(generated)}")
    print()
    return generated


def inspect_generated_tasks(task_dirs: list[Path]) -> None:
    """Inspect the generated task directories."""
    print("=" * 60)
    print("Step 4: Inspecting Generated Tasks")
    print("=" * 60)
    print()

    if not task_dirs:
        print("  No tasks generated!")
        return

    first = task_dirs[0]
    print(f"  {first.name}/")
    print("  ├── instruction.md")
    print("  ├── task.toml")
    print("  ├── environment/Dockerfile")
    print("  ├── tests/test.sh")
    print("  └── solution/solve.sh")
    print()

    for label, path in [
        ("instruction.md", first / "instruction.md"),
        ("task.toml", first / "task.toml"),
        ("Dockerfile", first / "environment" / "Dockerfile"),
        ("test.sh", first / "tests" / "test.sh"),
    ]:
        if path.exists():
            print(f"  --- {label} ---")
            for line in path.read_text().strip().split("\n"):
                print(f"    {line}")
            print()


def run_with_oracle(task_dirs: list[Path]) -> None:
    """Optionally run the generated tasks with the oracle agent."""
    print("=" * 60)
    print("Step 5: Running Tasks with the Oracle Agent")
    print("=" * 60)
    print()

    if not shutil.which("harbor"):
        print("  Harbor CLI not found. Install: uv tool install harbor")
        print("  To run manually:")
        for td in task_dirs:
            print(f"    $ harbor run -p {td} -a oracle")
        print()
        return

    docker_result = subprocess.run(["docker", "info"], capture_output=True, text=True, check=False)
    if docker_result.returncode != 0:
        print("  Docker not running. Start Docker Desktop to run tasks.")
        print()
        return

    first = task_dirs[0]
    print(f"Running oracle on: {first.name}")
    print(f"Command: harbor run -p {first} -a oracle")
    print()
    print("-" * 60)

    result = subprocess.run(
        ["harbor", "run", "-p", str(first), "-a", "oracle"],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent),
        timeout=300,
        check=False,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    print("-" * 60)
    status = "successfully" if result.returncode == 0 else f"with code {result.returncode}"
    print(f"\nOracle completed {status}.")
    print()
    print("To run all tasks:")
    print(f"  $ harbor run -p {task_dirs[0].parent} -a oracle")
    print()


def show_summary() -> None:
    """Display a summary of what was learned."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("Key takeaways:")
    print("  1. Adapters read benchmark data and generate Harbor tasks")
    print("  2. Use 'harbor adapter init' to scaffold a new adapter")
    print("  3. Core logic: for each instance, generate instruction.md,")
    print("     task.toml, Dockerfile, test.sh, solve.sh")
    print("  4. Test with oracle before running real agents")
    print("  5. Validate with 'harbor adapter review'")
    print()
    print("You have completed Module 9: Adapters!")
    print()
    print("Next module: Module 10 - Scaling & Cloud")


def main() -> None:
    """Run the custom-adapter lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 3, Module 9          #")
    print("#          Lesson 3: Building a Custom Adapter          #")
    print("########################################################")
    print()

    explain_adapter_scaffolding()
    show_source_data()
    task_dirs = run_conversion()
    inspect_generated_tasks(task_dirs)
    run_with_oracle(task_dirs)
    show_summary()


if __name__ == "__main__":
    main()
