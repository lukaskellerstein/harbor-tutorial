"""
Helper functions for the analyze-check lesson.

Contains the explanation and display functions that describe
harbor check and harbor analyze concepts and output formats.
"""

import json
from pathlib import Path

LESSON_DIR = Path(__file__).parent.resolve()
TASKS_DIR = LESSON_DIR / "tasks"
TRIALS_DIR = LESSON_DIR / "trials"
QUALITY_TASK_DIR = TASKS_DIR / "quality-task"
RUBRIC_PATH = LESSON_DIR / "rubric.toml"


def explain_harbor_check() -> None:
    """Explain the harbor check command and its purpose."""
    print("=" * 60)
    print("STEP 1: Understanding harbor check")
    print("=" * 60)
    print()
    print("The `harbor check` command validates task quality by having an")
    print("LLM agent read your task files and evaluate each criterion in a")
    print("rubric. It answers the question: 'Is this task well-constructed?'")
    print()
    print("How it works:")
    print("  1. Harbor reads your task (instruction.md, task.toml, tests/,")
    print("     solution/, Dockerfile)")
    print("  2. An LLM agent evaluates the task against each rubric criterion")
    print("  3. Each criterion produces: pass / fail / not_applicable")
    print("  4. Results are saved to check_report.json")
    print()
    print("Command syntax:")
    print("  harbor check <path-to-tasks> [options]")
    print()
    print("Key flags:")
    print("  -m, --model       Model to use (default: claude-sonnet-4-6)")
    print("  -r, --rubric      Custom rubric file (default: built-in 11-criteria)")
    print("  -a, --agent       Agent for evaluation (default: claude-code)")
    print("  -n, --n-concurrent  Max concurrent checks (default: 4)")
    print("  -i, --include-task-name  Only check tasks matching glob")
    print("  -x, --exclude-task-name  Skip tasks matching glob")
    print("  -l, --n-tasks     Max number of tasks to check")
    print()
    print("The default rubric checks 11 criteria:")
    print("  - behavior_in_task_description")
    print("  - behavior_in_tests")
    print("  - informative_test_structure")
    print("  - anti_cheating_measures")
    print("  - structured_data_schema")
    print("  - pinned_dependencies")
    print("  - typos")
    print("  - tests_or_solution_in_image")
    print("  - test_deps_in_image")
    print("  - hardcoded_solution")
    print("  - file_reference_mentioned")
    print()


def show_task_files() -> None:
    """Display the quality-task and its structure."""
    print("=" * 60)
    print("STEP 2: The quality-task Under Review")
    print("=" * 60)
    print()
    print("We have a sample task for the check/analyze tools to evaluate.")
    print("Here is its structure:")
    print()

    for item in sorted(QUALITY_TASK_DIR.rglob("*")):
        rel = item.relative_to(QUALITY_TASK_DIR)
        indent = "  " * (len(rel.parts) - 1)
        marker = "/" if item.is_dir() else ""
        print(f"  {indent}{item.name}{marker}")

    print()

    instruction_path = QUALITY_TASK_DIR / "instruction.md"
    if instruction_path.exists():
        print("-" * 40)
        print("instruction.md:")
        print("-" * 40)
        print(instruction_path.read_text().strip())
        print()

    dockerfile_path = QUALITY_TASK_DIR / "environment" / "Dockerfile"
    if dockerfile_path.exists():
        print("-" * 40)
        print("environment/Dockerfile:")
        print("-" * 40)
        print(dockerfile_path.read_text().strip())
        print()


def show_custom_rubric() -> None:
    """Display the custom rubric.toml and explain the format."""
    print("=" * 60)
    print("STEP 3: Custom Rubrics")
    print("=" * 60)
    print()
    print("You can define your own rubric to check criteria specific to")
    print("your project. A rubric is a TOML file with a [[criteria]] array.")
    print("Each criterion has three fields:")
    print()
    print("  name        - identifier (used as the key in results)")
    print("  description - short summary of what is being checked")
    print("  guidance    - detailed instructions for the LLM evaluator")
    print()
    print("Our custom rubric (rubric.toml) defines 5 criteria:")
    print()

    if RUBRIC_PATH.exists():
        print("-" * 40)
        print(RUBRIC_PATH.read_text().strip())
        print("-" * 40)
    print()

    print("To run harbor check with this rubric:")
    print()
    print(f"  harbor check {TASKS_DIR} -r {RUBRIC_PATH} \\")
    print("    -m anthropic/claude-sonnet-4-5-20250929")
    print()
    print("NOTE: Running harbor check requires an LLM API key because the")
    print("evaluator agent makes LLM calls to assess each criterion.")
    print()


def show_check_output_format() -> None:
    """Show what harbor check output looks like."""
    print("=" * 60)
    print("STEP 4: harbor check Output Format")
    print("=" * 60)
    print()
    print("Each criterion produces a QualityCheckModel with two fields:")
    print("  - outcome: 'pass', 'fail', or 'not_applicable'")
    print("  - explanation: the LLM's reasoning for the outcome")
    print()
    print("Example output (check_report.json):")
    print()

    example: dict = {
        "results": [
            {
                "task_name": "quality-task",
                "checks": {
                    "instruction_completeness": {
                        "outcome": "pass",
                        "explanation": "All five test behaviors are described.",
                    },
                    "test_coverage": {
                        "outcome": "pass",
                        "explanation": "Tests cover the core operations.",
                    },
                    "solution_correctness": {
                        "outcome": "pass",
                        "explanation": "Solution implements all requirements.",
                    },
                    "environment_setup": {
                        "outcome": "pass",
                        "explanation": "Dockerfile creates correct setup.",
                    },
                    "anti_cheating": {
                        "outcome": "pass",
                        "explanation": "Tests/solution are not in the image.",
                    },
                },
                "cost_usd": 0.0142,
            }
        ]
    }
    print(json.dumps(example, indent=2))
    print()
    print("In the terminal, harbor check renders this as a Rich table:")
    print()
    print("  +----------------------------+---------+-------------------+")
    print("  | Check                      | Outcome | Explanation       |")
    print("  +----------------------------+---------+-------------------+")
    print("  | Instruction Completeness   | pass    | All five test ... |")
    print("  | Test Coverage              | pass    | Tests cover ...   |")
    print("  | Solution Correctness       | pass    | The solution ...  |")
    print("  | Environment Setup          | pass    | Dockerfile ...    |")
    print("  | Anti Cheating              | pass    | Tests and ...     |")
    print("  +----------------------------+---------+-------------------+")
    print()


def explain_harbor_analyze() -> None:
    """Explain the harbor analyze command."""
    print("=" * 60)
    print("STEP 5: Understanding harbor analyze")
    print("=" * 60)
    print()
    print("While `harbor check` validates task quality BEFORE running")
    print("trials, `harbor analyze` inspects trial trajectories AFTER")
    print("trials have completed. It answers: 'Did the agent behave")
    print("correctly during this trial?'")
    print()
    print("How it works:")
    print("  1. Harbor reads the agent trajectory (agent/trajectory.json)")
    print("  2. It also reads the task definition and trial results")
    print("  3. An LLM evaluates the trial against each rubric criterion")
    print("  4. Results include a summary and per-criterion pass/fail")
    print("  5. Output is saved to analysis.json")
    print()
    print("Command syntax:")
    print("  harbor analyze <path-to-trial-or-job> [options]")
    print()
    print("Key flags:")
    print("  -m, --model       Model to use (default: claude-haiku-4-5)")
    print("  -r, --rubric      Custom rubric file (default: built-in)")
    print("  -a, --agent       Agent for evaluation (default: claude-code)")
    print("  --passing         Only analyze passing trials (reward=1.0)")
    print("  --failing         Only analyze failing trials (reward<1.0)")
    print("  -l, --n-trials    Max number of trials to analyze")
    print("  -n, --n-concurrent  Max concurrent analyses (default: 4)")
    print()
    print("Default analyze rubric checks 2 criteria:")
    print()
    print("  reward_hacking     - Did the agent hack the tests or cheat?")
    print("                       Looks for: modifications to test files,")
    print("                       writes to reward.txt, copying from solution/")
    print()
    print("  task_specification - Are the instructions sufficient for success?")
    print("                       Compares instruction.md against test expectations")
    print()


def show_analyze_command(trial_dir: str | None) -> None:
    """Show how to run harbor analyze on the trial data."""
    print("=" * 60)
    print("STEP 7: Running harbor analyze")
    print("=" * 60)
    print()

    target = trial_dir if trial_dir else str(TRIALS_DIR)
    print("To analyze the trial trajectory, run:")
    print()
    print(f"  harbor analyze {target} \\")
    print("    -m anthropic/claude-haiku-4-5-20250929")
    print()
    print("NOTE: Running harbor analyze requires an LLM API key because")
    print("the evaluator agent makes LLM calls to assess the trajectory.")
    print()
    print("The output is saved to analysis.json inside the job directory.")
    print()
    print("Example analysis output:")
    print()

    example: dict = {
        "results": [
            {
                "trial_name": "quality-task_oracle_0",
                "summary": "The oracle agent ran the solution script. All 5 tests passed with reward 1.0.",
                "checks": {
                    "reward_hacking": {
                        "outcome": "pass",
                        "explanation": "Agent solved legitimately via solution script.",
                    },
                    "task_specification": {
                        "outcome": "pass",
                        "explanation": "Instructions clearly specify all behavior.",
                    },
                },
                "cost_usd": 0.0038,
            }
        ]
    }
    print(json.dumps(example, indent=2))
    print()
    print("You can filter which trials to analyze:")
    print()
    print(f"  harbor analyze {target} --passing   # only reward=1.0 trials")
    print(f"  harbor analyze {target} --failing   # only reward<1.0 trials")
    print(f"  harbor analyze {target} -l 5        # analyze at most 5 trials")
    print()
