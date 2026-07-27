"""
Lesson 1: Task Directory Structure

This lesson walks through the anatomy of a Harbor task directory,
explaining each component and its role in the evaluation pipeline.
"""

from pathlib import Path

from components import COMPONENTS


def show_directory_tree(task_dir: Path) -> None:
    """Display the task directory as an ASCII tree."""
    print("=" * 60)
    print("Step 1: Task Directory Structure")
    print("=" * 60)
    print()
    print("A Harbor task is a directory with five components:")
    print()
    print(f"  {task_dir.name}/")
    print("  ├── instruction.md         # What the agent must do")
    print("  ├── task.toml              # Configuration and metadata")
    print("  ├── environment/")
    print("  │   └── Dockerfile         # Container definition")
    print("  ├── tests/")
    print("  │   └── test.sh            # Verifier (writes reward 0-1)")
    print("  └── solution/")
    print("      └── solve.sh           # Reference solution (optional)")
    print()

    expected = [
        "instruction.md", "task.toml", "environment/Dockerfile",
        "tests/test.sh", "solution/solve.sh",
    ]
    all_present = True
    for rel_path in expected:
        exists = (task_dir / rel_path).exists()
        if not exists:
            all_present = False
        print(f"  {'[OK]' if exists else '[MISSING]'} {rel_path}")

    print()
    print("  All five components are present." if all_present
          else "  WARNING: Some components are missing!")
    print()


def show_component(task_dir: Path, component: dict[str, str]) -> None:
    """Display a single task component with its contents."""
    file_path = task_dir / component["file"]

    print("-" * 60)
    print(f"  Component: {component['title']}")
    print(f"  File:      {component['file']}")
    print(f"  Purpose:   {component['description']}")
    print("-" * 60)

    if file_path.exists():
        content = file_path.read_text().strip()
        print()
        for line in content.splitlines():
            print(f"    {line}")
        print()
    else:
        print(f"\n    [File not found: {file_path}]\n")


def walk_components(task_dir: Path) -> None:
    """Walk through each component, explaining its role."""
    print("=" * 60)
    print("Step 2: Examining Each Component")
    print("=" * 60)
    print()
    print("Let's look at each file in the count-words task.")
    print("This task asks an agent to create a Python script that")
    print("reads /app/input.txt and prints the number of words.")
    print()

    for i, component in enumerate(COMPONENTS, start=1):
        print(f"  [{i}/5]")
        show_component(task_dir, component)


def explain_evaluation_pipeline() -> None:
    """Explain how the components connect during evaluation."""
    print("=" * 60)
    print("Step 3: How the Components Connect")
    print("=" * 60)
    print()
    print("During evaluation, Harbor uses these files in order:")
    print()
    print("  1. BUILD      environment/Dockerfile")
    print("     Harbor builds a Docker image and starts a container.")
    print()
    print("  2. INSTRUCT   instruction.md")
    print("     The agent receives the instruction text.")
    print()
    print("  3. SOLVE      (agent works inside the container)")
    print("     The agent reads, writes, and executes commands.")
    print()
    print("  4. VERIFY     tests/test.sh")
    print("     After the agent finishes, Harbor runs test.sh.")
    print()
    print("  5. REWARD     /logs/verifier/reward.txt")
    print("     test.sh writes a float (0 to 1) to this path.")
    print()
    print("  The solution/ directory is NOT used during normal")
    print("  evaluation -- only by the oracle agent.")
    print()


def explain_task_toml() -> None:
    """Provide extra detail on task.toml fields."""
    print("=" * 60)
    print("Step 4: task.toml Deep Dive")
    print("=" * 60)
    print()
    print("Key sections in task.toml:")
    print()
    print("  [task]")
    print('    name = "org/task-name"   # Unique identifier')
    print()
    print("  [metadata]")
    print("    difficulty = \"easy\"       # easy, medium, hard")
    print("    category = \"programming\" # Task category")
    print("    tags = [\"python\"]        # Searchable tags")
    print()
    print("  [agent]")
    print("    timeout_sec = 120.0      # Max seconds for agent")
    print()
    print("  [verifier]")
    print("    timeout_sec = 120.0      # Max seconds for test.sh")
    print()
    print("  [environment]")
    print("    build_timeout_sec = 600.0  # Max seconds to build")
    print()
    print("  Timeouts prevent runaway agents and slow tests from")
    print("  blocking your evaluation pipeline.")
    print()


def show_summary() -> None:
    """Display the lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("A Harbor task directory has five components:")
    print()
    print("  instruction.md   -- What the agent must do")
    print("  task.toml        -- Configuration: name, timeouts, metadata")
    print("  environment/     -- Dockerfile defining the container")
    print("  tests/           -- Verifier script that writes reward (0-1)")
    print("  solution/        -- Reference solution for validation")
    print()
    print("The evaluation flow is:")
    print("  Build container -> Give instruction -> Agent works ->")
    print("  Run test.sh -> Read reward from /logs/verifier/reward.txt")
    print()
    print("Next lesson: lesson-2-create-a-task (build your own task from scratch)")


def main() -> None:
    """Run the task-anatomy lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Module 2, Lesson 1         #")
    print("#          Task Directory Structure                     #")
    print("########################################################")
    print()

    task_dir = Path(__file__).parent / "tasks" / "example-task"

    show_directory_tree(task_dir)
    walk_components(task_dir)
    explain_evaluation_pipeline()
    explain_task_toml()
    show_summary()


if __name__ == "__main__":
    main()
