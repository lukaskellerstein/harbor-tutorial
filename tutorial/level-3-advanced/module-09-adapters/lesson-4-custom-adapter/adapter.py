"""
Custom Adapter — Converts a CSV of coding challenges into Harbor task directories.

This module demonstrates the core logic of a Harbor adapter: reading
benchmark data from a source format and generating standard Harbor
task directories with instruction.md, task.toml, Dockerfile, test.sh,
and solve.sh.
"""

import csv
import textwrap
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Challenge:
    """A single coding challenge from the CSV."""

    id: str
    instruction: str
    expected_output: str
    difficulty: str


def load_challenges(csv_path: Path) -> list[Challenge]:
    """Load coding challenges from a CSV file."""
    challenges: list[Challenge] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            challenges.append(
                Challenge(
                    id=row["id"].strip(),
                    instruction=row["instruction"].strip(),
                    expected_output=row["expected_output"].strip(),
                    difficulty=row["difficulty"].strip(),
                )
            )
    return challenges


def generate_instruction(challenge: Challenge) -> str:
    """Generate instruction.md content for a challenge."""
    return f"{challenge.instruction}\n"


def generate_task_toml(challenge: Challenge, dataset_name: str) -> str:
    """Generate task.toml content for a challenge."""
    return textwrap.dedent(f"""\
        version = "1.0"

        [task]
        name = "{dataset_name}/{challenge.id}"

        [metadata]
        difficulty = "{challenge.difficulty}"
        category = "programming"
        tags = ["python", "coding-challenge"]

        [agent]
        timeout_sec = 300.0

        [verifier]
        timeout_sec = 60.0

        [environment]
        build_timeout_sec = 120.0
    """)


def generate_dockerfile(challenge: Challenge) -> str:
    """Generate a Dockerfile for the task environment."""
    # Base setup: Python, a working directory, and any input files
    dockerfile = textwrap.dedent("""\
        FROM python:3.12-slim

        RUN useradd -m -s /bin/bash user
        WORKDIR /home/user
    """)

    # Add input files for tasks that need them
    if challenge.id == "word-count":
        dockerfile += textwrap.dedent("""\

        # Create input file for word-count challenge
        RUN echo "The quick brown fox jumps over the lazy dog near the river bank under the old oak tree beside the wooden fence along the dusty road past the red barn where the rooster crows every morning at dawn" > /home/user/input.txt
        """)
    elif challenge.id == "csv-parser":
        dockerfile += textwrap.dedent("""\

        # Create input CSV for csv-parser challenge
        RUN printf "name,age,city\\nAlice,30,New York\\nBob,22,London\\nCharlie,28,Paris\\nDiana,19,Tokyo\\n" > /home/user/data.csv
        """)

    dockerfile += textwrap.dedent("""\

        RUN chown -R user:user /home/user
        USER user
    """)
    return dockerfile


def generate_test_script(challenge: Challenge) -> str:
    """Generate test.sh that verifies the agent's solution."""
    return textwrap.dedent(f"""\
        #!/bin/bash
        # Test script for: {challenge.id}
        # Runs the agent's solution and checks the output.

        set -e

        REWARD_FILE="/logs/verifier/reward.txt"
        mkdir -p /logs/verifier

        # Run the solution and capture output
        cd /home/user
        ACTUAL=$(python solution.py 2>&1) || true

        # Check if expected output is present
        if echo "$ACTUAL" | grep -q "{challenge.expected_output}"; then
            echo "PASS: Output contains expected value '{challenge.expected_output}'"
            echo "1.0" > "$REWARD_FILE"
        else
            echo "FAIL: Expected output to contain '{challenge.expected_output}'"
            echo "Actual output:"
            echo "$ACTUAL"
            echo "0.0" > "$REWARD_FILE"
        fi
    """)


def generate_solve_script(challenge: Challenge) -> str:
    """Generate solve.sh — a reference solution for the oracle agent."""
    if challenge.id == "fizzbuzz":
        solution_code = textwrap.dedent("""\
            for i in range(1, 31):
                if i % 15 == 0:
                    print("FizzBuzz")
                elif i % 3 == 0:
                    print("Fizz")
                elif i % 5 == 0:
                    print("Buzz")
                else:
                    print(i)
        """)
    elif challenge.id == "word-count":
        solution_code = textwrap.dedent("""\
            with open("/home/user/input.txt") as f:
                words = f.read().split()
            print(len(words))
        """)
    elif challenge.id == "csv-parser":
        solution_code = textwrap.dedent("""\
            import csv
            with open("/home/user/data.csv") as f:
                reader = csv.DictReader(f)
                names = [row["name"] for row in reader if int(row["age"]) > 25]
            for name in sorted(names):
                print(name)
        """)
    else:
        solution_code = '# No reference solution available\nprint("not implemented")\n'

    return textwrap.dedent(f"""\
        #!/bin/bash
        # Reference solution for: {challenge.id}
        cat > /home/user/solution.py << 'PYEOF'
        {solution_code.rstrip()}
        PYEOF
        cd /home/user && python solution.py
    """)


def generate_task_directory(
    challenge: Challenge,
    output_dir: Path,
    dataset_name: str,
) -> Path:
    """Generate a complete Harbor task directory for a challenge."""
    task_dir = output_dir / challenge.id

    # Create subdirectories
    (task_dir / "environment").mkdir(parents=True, exist_ok=True)
    (task_dir / "tests").mkdir(parents=True, exist_ok=True)
    (task_dir / "solution").mkdir(parents=True, exist_ok=True)

    # Write all task files
    (task_dir / "instruction.md").write_text(generate_instruction(challenge), encoding="utf-8")
    (task_dir / "task.toml").write_text(generate_task_toml(challenge, dataset_name), encoding="utf-8")
    (task_dir / "environment" / "Dockerfile").write_text(generate_dockerfile(challenge), encoding="utf-8")

    test_script = task_dir / "tests" / "test.sh"
    test_script.write_text(generate_test_script(challenge), encoding="utf-8")
    test_script.chmod(0o755)

    solve_script = task_dir / "solution" / "solve.sh"
    solve_script.write_text(generate_solve_script(challenge), encoding="utf-8")
    solve_script.chmod(0o755)

    return task_dir


def run_adapter(
    csv_path: Path,
    output_dir: Path,
    dataset_name: str = "coding-challenges",
) -> list[Path]:
    """
    Main adapter entry point: convert a CSV of challenges into
    Harbor task directories.

    Returns a list of generated task directory paths.
    """
    challenges = load_challenges(csv_path)
    generated: list[Path] = []

    for challenge in challenges:
        task_dir = generate_task_directory(challenge, output_dir, dataset_name)
        generated.append(task_dir)

    return generated
