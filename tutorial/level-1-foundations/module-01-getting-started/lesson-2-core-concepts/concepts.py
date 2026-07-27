"""
Core concept explanations for the Harbor tutorial.
Each function prints a detailed explanation of one Harbor concept.
"""

from pathlib import Path


def explain_task() -> None:
    """Explain what a Task is and show its directory structure."""
    print("=" * 60)
    print("Concept 1: TASK")
    print("=" * 60)
    print()
    print("A Task is the fundamental unit of evaluation in Harbor.")
    print("It defines WHAT an agent should do, WHERE it works, and")
    print("HOW success is measured.")
    print()
    print("Every task is a directory with this structure:")
    print()
    print("  my-task/")
    print("  ├── instruction.md         # Natural language instruction")
    print("  │                           # for the agent")
    print("  ├── task.toml              # Configuration & metadata")
    print("  │                           # (timeouts, difficulty, tags)")
    print("  ├── environment/")
    print("  │   └── Dockerfile         # Container definition where")
    print("  │                           # the agent will work")
    print("  ├── tests/")
    print("  │   └── test.sh            # Verifier script that checks")
    print("  │                           # the agent's work and writes")
    print("  │                           # a reward (0-1) to:")
    print("  │                           # /logs/verifier/reward.txt")
    print("  └── solution/")
    print("      └── solve.sh           # Reference solution (used by")
    print("                              # the oracle agent)")
    print()
    print("Think of a task as an exam question: it has a prompt,")
    print("a workspace, an answer key, and a grading rubric.")
    print()


def explain_dataset() -> None:
    """Explain what a Dataset is."""
    print("=" * 60)
    print("Concept 2: DATASET")
    print("=" * 60)
    print()
    print("A Dataset is a collection of Tasks, usually grouped by")
    print("theme or benchmark.")
    print()
    print("  my-dataset/")
    print("  ├── task-001/")
    print("  │   ├── instruction.md")
    print("  │   ├── task.toml")
    print("  │   ├── environment/")
    print("  │   ├── tests/")
    print("  │   └── solution/")
    print("  ├── task-002/")
    print("  │   └── ...")
    print("  └── task-003/")
    print("      └── ...")
    print()
    print("Harbor can run evaluations against:")
    print("  - A local dataset:      harbor run -p path/to/dataset ...")
    print("  - A registered dataset: harbor run -d org/name ...")
    print()
    print("Use 'harbor dataset list' to see available registered datasets.")
    print()


def explain_agent() -> None:
    """Explain what an Agent is."""
    print("=" * 60)
    print("Concept 3: AGENT")
    print("=" * 60)
    print()
    print("An Agent is the program being evaluated. It reads the")
    print("task instruction and attempts to complete the work inside")
    print("the container environment.")
    print()
    print("Harbor supports 37+ built-in agents:")
    print()
    print("  Production agents:")
    print("    claude-code     - Anthropic's Claude Code CLI")
    print("    openhands       - OpenHands autonomous agent")
    print("    aider           - Aider coding assistant")
    print("    codex           - OpenAI Codex CLI")
    print("    gemini-cli      - Google's Gemini CLI")
    print()
    print("  Utility agents:")
    print("    oracle          - Runs the reference solution (solve.sh)")
    print("    nop             - Does nothing (tests environment setup)")
    print()
    print("  Custom agents:")
    print("    BaseAgent           - External agent (sends commands in)")
    print("    BaseInstalledAgent  - Installs itself inside the container")
    print()
    print("Run an evaluation with a specific agent:")
    print("  harbor run -p path/to/task -a claude-code -m anthropic/claude-sonnet-4-5-20250929")
    print()


def explain_environment() -> None:
    """Explain what an Environment is."""
    print("=" * 60)
    print("Concept 4: ENVIRONMENT")
    print("=" * 60)
    print()
    print("An Environment is the isolated container where an agent")
    print("works. It is built from the task's Dockerfile and provides")
    print("a sandboxed workspace.")
    print()
    print("Environment types:")
    print("  docker   - Local Docker containers (default)")
    print("  daytona  - Daytona cloud sandboxes")
    print("  modal    - Modal cloud compute")
    print("  e2b      - E2B cloud sandboxes")
    print()
    print("The agent interacts with the environment via commands:")
    print()
    print("  # In a custom agent:")
    print("  result = await environment.exec(command='ls -la')")
    print("  result = await environment.exec(command='cat hello.txt')")
    print()
    print("Each trial gets a fresh container — agents cannot cheat")
    print("by reusing state from previous attempts.")
    print()


def explain_trial() -> None:
    """Explain what a Trial is."""
    print("=" * 60)
    print("Concept 5: TRIAL")
    print("=" * 60)
    print()
    print("A Trial is a single agent attempt at a single task.")
    print("It is the atomic unit of measurement.")
    print()
    print("A trial produces:")
    print("  - A reward (0 to 1): written by the test script to")
    print("    /logs/verifier/reward.txt")
    print("  - Agent trajectory: the commands and outputs during")
    print("    the agent's work")
    print("  - config.json: trial configuration snapshot")
    print("  - result.json: trial outcome and metrics")
    print()
    print("Run a single trial:")
    print("  harbor trial start -p path/to/task -a oracle")
    print()
    print("A reward of 1 means the agent fully solved the task.")
    print("A reward of 0 means it failed.")
    print("Partial credit (e.g., 0.5) is also possible.")
    print()


def explain_job() -> None:
    """Explain what a Job is."""
    print("=" * 60)
    print("Concept 6: JOB")
    print("=" * 60)
    print()
    print("A Job is a collection of trials — typically running one")
    print("or more agents against one or more tasks.")
    print()
    print("Jobs are configured via job.yaml or CLI flags:")
    print()
    print("  # CLI — run all tasks in a dataset:")
    print("  harbor run -p path/to/dataset -a claude-code -m anthropic/claude-sonnet-4-5-20250929")
    print()
    print("  # Config file — full control:")
    print("  harbor run -c job.yaml")
    print()
    print("Example job.yaml:")
    print("  datasets:")
    print("    - path: path/to/dataset")
    print("  agents:")
    print("    - name: claude-code")
    print("      model_name: anthropic/claude-sonnet-4-5-20250929")
    print("  environment:")
    print("    type: docker")
    print("  orchestrator:")
    print("    type: local")
    print("    n_concurrent_trials: 4")
    print()
    print("Results are stored in the jobs/ directory.")
    print()


def show_relationships() -> None:
    """Show how the core concepts relate to each other."""
    print("=" * 60)
    print("How Everything Fits Together")
    print("=" * 60)
    print()
    print("Here is how the core concepts relate:")
    print()
    print("  ┌─────────────────────────────────────────────┐")
    print("  │                    JOB                      │")
    print("  │                                             │")
    print("  │  ┌─────────┐  ┌─────────┐  ┌─────────┐    │")
    print("  │  │ Trial 1 │  │ Trial 2 │  │ Trial 3 │    │")
    print("  │  └────┬────┘  └────┬────┘  └────┬────┘    │")
    print("  │       │            │            │          │")
    print("  └───────┼────────────┼────────────┼──────────┘")
    print("          │            │            │")
    print("          v            v            v")
    print("  ┌──────────────────────────────────────┐")
    print("  │  Each Trial combines:                │")
    print("  │                                      │")
    print("  │  AGENT  +  TASK  +  ENVIRONMENT      │")
    print("  │    │         │         │              │")
    print("  │    │         │         └─> Dockerfile │")
    print("  │    │         ├─> instruction.md       │")
    print("  │    │         ├─> task.toml             │")
    print("  │    │         ├─> tests/test.sh         │")
    print("  │    │         └─> solution/solve.sh     │")
    print("  │    │                                  │")
    print("  │    └─> Reads instruction, executes    │")
    print("  │        commands in the environment    │")
    print("  └──────────────────────────────────────┘")
    print()
    print("  DATASET = collection of TASKs")
    print("  JOB     = collection of TRIALs")
    print("  TRIAL   = one AGENT attempt at one TASK in one ENVIRONMENT")
    print()


def explore_example_task() -> None:
    """Explore the hello-world task from the previous lesson."""
    print("=" * 60)
    print("Exploring an Example Task")
    print("=" * 60)

    lesson_dir = Path(__file__).parent.parent / "hello-harbor" / "tasks" / "hello-world"
    if not lesson_dir.exists():
        print()
        print(f"  Task directory not found at: {lesson_dir}")
        print("  Complete the hello-harbor lesson first to create it.")
        print()
        return

    print()
    print(f"Inspecting: {lesson_dir}")
    print()

    files_info: dict[str, str] = {
        "instruction.md": "The task the agent must complete",
        "task.toml": "Configuration: name, difficulty, timeouts",
        "environment/Dockerfile": "Container definition for the workspace",
        "tests/test.sh": "Verifier script that checks the agent's work",
        "solution/solve.sh": "Reference solution (used by oracle agent)",
    }

    for rel_path, description in files_info.items():
        file_path = lesson_dir / rel_path
        if file_path.exists():
            content = file_path.read_text().strip()
            print(f"  {rel_path}")
            print(f"  Purpose: {description}")
            print(f"  Content:")
            for line in content.split("\n"):
                print(f"    | {line}")
            print()
