"""
Lesson: Oracle & Nop Agents
============================
Learn how to use Harbor's two utility agents -- oracle and nop -- to
validate that your tasks' solutions and tests work correctly.
"""

import sys
from pathlib import Path

from helpers import (
    check_prerequisites,
    get_agent_name,
    get_exception,
    get_latest_trial_result,
    get_reward,
    run_harbor_command,
)


def explain_oracle_agent() -> None:
    """Explain what the oracle agent does and why it matters."""
    print("=" * 60)
    print("Step 1: The Oracle Agent")
    print("=" * 60)
    print("\nThe oracle agent runs solution/solve.sh to validate tasks.\n")
    print("How it works:")
    print("  1. Uploads solution/solve.sh into the container")
    print("  2. Makes the script executable and runs it")
    print("  3. The verifier (tests/test.sh) checks the result\n")
    print("If oracle gets reward 1.0, it proves:")
    print("  - Your solution script works correctly")
    print("  - Your test script correctly validates the solution")
    print("  - Your Dockerfile sets up the right environment\n")
    print("No API keys or model needed.\n")


def explain_nop_agent() -> None:
    """Explain what the nop agent does and why it matters."""
    print("=" * 60)
    print("Step 2: The Nop Agent")
    print("=" * 60)
    print("\nThe nop (no-operation) agent does absolutely nothing.\n")
    print("How it works:")
    print("  1. Agent setup: does nothing")
    print("  2. Agent run: does nothing")
    print("  3. The verifier runs against the untouched environment\n")
    print("If nop gets reward 0.0, it proves:")
    print("  - Your tests correctly detect unsolved tasks")
    print("  - The environment does not leak the answer\n")
    print("If nop gets reward > 0.0:")
    print("  - Tests may be too lenient")
    print("  - Dockerfile may accidentally contain the answer\n")


def show_task_under_test() -> None:
    """Display the task we will validate."""
    print("=" * 60)
    print("Step 3: Our task under test")
    print("=" * 60)

    task_dir = Path("tasks/validated-task")
    instruction = (task_dir / "instruction.md").read_text().strip()
    print(f"\nTask: {task_dir.name}")
    print(f"Instruction:\n  {instruction.replace(chr(10), chr(10) + '  ')}\n")

    solution = (task_dir / "solution" / "solve.sh").read_text().strip()
    print("Solution (solve.sh):")
    for line in solution.split("\n"):
        print(f"  {line}")
    print()


def run_oracle_trial() -> dict | None:
    """Run the task with the oracle agent and return results."""
    print("=" * 60)
    print("Step 4: Running with the oracle agent")
    print("=" * 60)
    print("\nExpected: reward 1.0 (solution + tests work)\n")
    print("Running oracle trial...")
    print("-" * 60)

    cmd = [
        "harbor", "trial", "start",
        "-p", "tasks/validated-task", "-a", "oracle",
        "--delete", "--trials-dir", "trials/oracle",
    ]

    run_harbor_command(cmd)
    print("-" * 60)

    return get_latest_trial_result("trials/oracle")


def run_nop_trial() -> dict | None:
    """Run the task with the nop agent and return results."""
    print()
    print("=" * 60)
    print("Step 5: Running with the nop agent")
    print("=" * 60)
    print("\nExpected: reward 0.0 (tests reject unsolved state)\n")
    print("Running nop trial...")
    print("-" * 60)

    cmd = [
        "harbor", "trial", "start",
        "-p", "tasks/validated-task", "-a", "nop",
        "--delete", "--trials-dir", "trials/nop",
    ]

    run_harbor_command(cmd)
    print("-" * 60)

    return get_latest_trial_result("trials/nop")


def compare_results(oracle_result: dict | None, nop_result: dict | None) -> None:
    """Compare oracle and nop results side by side."""
    print()
    print("=" * 60)
    print("Step 6: Comparing results")
    print("=" * 60)
    print()

    print(f"  {'':20} {'Oracle':>15} {'Nop':>15}")
    print(f"  {'-' * 20} {'-' * 15} {'-' * 15}")
    print(f"  {'Agent':<20} {get_agent_name(oracle_result):>15} {get_agent_name(nop_result):>15}")
    print(f"  {'Reward':<20} {get_reward(oracle_result):>15} {get_reward(nop_result):>15}")
    print(f"  {'Exception':<20} {get_exception(oracle_result):>15} {get_exception(nop_result):>15}")

    oracle_ok = get_reward(oracle_result) == "1.0"
    nop_ok = get_reward(nop_result) == "0.0"

    print()
    if oracle_ok and nop_ok:
        print("  VALIDATION PASSED")
        print("  - Oracle got 1.0: solution and tests are correct")
        print("  - Nop got 0.0: tests correctly reject unsolved tasks")
        print("  - This task is ready for real agent evaluation!")
    elif not oracle_ok:
        print("  VALIDATION ISSUE: Oracle did not get 1.0")
        print("  - Check solution/solve.sh and tests/test.sh")
    elif not nop_ok:
        print("  VALIDATION ISSUE: Nop did not get 0.0")
        print("  - Tests may be too lenient or Dockerfile leaks the answer")
    print()


def explain_validation_workflow() -> None:
    """Explain the recommended validation workflow."""
    print("=" * 60)
    print("Step 7: The task validation workflow")
    print("=" * 60)
    print("\nBefore running real agents, always validate:\n")
    print("  Step 1: Run with nop agent")
    print("    harbor trial start -p <task> -a nop --delete")
    print("    Expected: reward 0.0\n")
    print("  Step 2: Run with oracle agent")
    print("    harbor trial start -p <task> -a oracle --delete")
    print("    Expected: reward 1.0\n")
    print("  Step 3: Both pass? Run real agents:")
    print("    harbor run -p <task> -a claude-code -m anthropic/claude-sonnet-4-5-20250929 --delete\n")


def recap() -> None:
    """Summarize what was learned."""
    print("=" * 60)
    print("Recap")
    print("=" * 60)
    print("\nIn this lesson you learned:\n")
    print("  1. Oracle runs solution/solve.sh (expect reward 1.0)")
    print("  2. Nop does nothing (expect reward 0.0)")
    print("  3. Always validate with both before real evaluations")
    print("  4. This catches task authoring bugs early")
    print("\nYou have completed Module 3: Running Evaluations!")
    print("Next: Module 4 - Building Custom Agents\n")


def main() -> None:
    """Run the utility-agents lesson."""
    print()
    print("=" * 60)
    print("  Harbor Tutorial - Module 3, Lesson 4")
    print("  Oracle & Nop Agents")
    print("=" * 60)
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_oracle_agent()
    explain_nop_agent()
    show_task_under_test()

    oracle_result = run_oracle_trial()
    nop_result = run_nop_trial()

    compare_results(oracle_result, nop_result)
    explain_validation_workflow()
    recap()


if __name__ == "__main__":
    main()
