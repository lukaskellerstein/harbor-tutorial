"""
Module 8, Lesson 3: RewardKit -- Programmatic Criteria

Replaces hand-written bash verifiers with declarative criteria files, and shows
the per-criterion breakdown you get for free in reward-details.json.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from criteria_catalogue import print_catalogue
from results import (
    latest_job_dir,
    reward_details,
    run_task,
    show_criteria,
    show_rewards,
    trial_rewards,
)

LESSON_DIR = Path(__file__).parent


def check_prerequisites() -> bool:
    """Verify Docker and Harbor are available."""
    print("=" * 60)
    print("Checking Prerequisites")
    print("=" * 60)

    docker_ok = shutil.which("docker") is not None
    harbor_ok = shutil.which("harbor") is not None
    docker_running = subprocess.run(["docker", "info"], capture_output=True, text=True, check=False).returncode == 0

    print(f"  Docker CLI:     {'[OK]' if docker_ok else '[MISSING]'}")
    print(f"  Docker running: {'[OK]' if docker_running else '[NOT RUNNING]'}")
    print(f"  Harbor CLI:     {'[OK]' if harbor_ok else '[MISSING]'}")
    print()

    if not (docker_ok and docker_running and harbor_ok):
        print("  Prerequisites not met. Fix the issues above.")
        return False
    return True


def _code_lines(path: Path) -> list[str]:
    """Read a criteria file, dropping the module docstring and imports.

    Comments survive -- in a criteria file they are the explanation.
    """
    lines = path.read_text().splitlines()
    body: list[str] = []
    in_docstring = False
    seen_docstring = False

    for line in lines:
        if not seen_docstring and line.startswith('"""'):
            in_docstring = True
            seen_docstring = True
            # Handle a one-line docstring.
            if line.count('"""') == 2:
                in_docstring = False
            continue
        if in_docstring:
            if '"""' in line:
                in_docstring = False
            continue
        if line.startswith(("import ", "from ")):
            continue
        if not line.strip():
            continue
        body.append(line)
    return body


def explain_rewardkit() -> None:
    """Step 1: what RewardKit is and how it is invoked."""
    print("=" * 60)
    print("Step 1: What RewardKit Is")
    print("=" * 60)
    print()
    print("  A package that turns a directory of criteria into a reward.")
    print("  Your test.sh stops being a script and becomes one line:")
    print()
    print("    #!/bin/bash")
    print("    uvx --from 'harbor-rewardkit==0.1.*' rewardkit /tests")
    print()
    print("  Mind the `--from`. The PACKAGE is harbor-rewardkit but the")
    print("  EXECUTABLE is rewardkit, so plain `uvx harbor-rewardkit` fails --")
    print("  uvx would look for a command named after the package. Some")
    print("  published docs show that broken form.")
    print()
    print("  RewardKit then:")
    print("    1. discovers every criterion under /tests")
    print("    2. runs them against the workspace (/app by default)")
    print("    3. writes /logs/verifier/reward.json      <- the scores")
    print("       and    /logs/verifier/reward-details.json  <- the breakdown")
    print()
    print("  No subdirectories under tests/ means a FLAT layout: everything")
    print('  contributes to a single reward named "reward".')
    print()


def show_catalogue() -> None:
    """Step 2: the built-in criteria."""
    print("=" * 60)
    print("Step 2: The Built-in Criteria")
    print("=" * 60)
    print()
    print("  23 of them, no imports beyond `import rewardkit as rk`:")
    print()
    print_catalogue()
    print("  Return-type rule: a criterion returning bool scores 1.0 or 0.0.")
    print("  One returning a number is used VERBATIM and is NOT clamped -- a")
    print("  criterion that returns 3.7 contributes 3.7 (with a warning).")
    print()


def step_wordstats() -> None:
    """Step 3: run the criteria tour task."""
    print("=" * 60)
    print("Step 3: Criteria in Practice")
    print("=" * 60)
    print()
    print("  tasks/wordstats/tests/checks.py:")
    print()
    checks = LESSON_DIR / "tasks" / "wordstats" / "tests" / "checks.py"
    for line in _code_lines(checks):
        print(f"    {line}")
    print()
    print("  Note the weights. They are RELATIVE, not percentages: correctness")
    print("  criteria at 3.0 outweigh the existence check at 1.0, so a script")
    print("  that runs but computes garbage scores well below one that works.")
    print()
    print("  And note what the criteria do NOT do: none of them depends on")
    print("  another one having run first. Criteria execute CONCURRENTLY, in")
    print("  an asyncio TaskGroup -- registration order is not execution order.")
    print('  Writing json_key_equals("results.json", ...) and expecting the')
    print("  command_succeeds above it to have created that file is a race, and")
    print("  it loses more often than it wins.")
    print()

    if not run_task(LESSON_DIR, "wordstats"):
        print("  Trial failed. Skipping analysis.")
        return

    job_dir = latest_job_dir(LESSON_DIR)
    if job_dir is None:
        return

    show_rewards("reward.json (what Harbor records):", trial_rewards(job_dir))
    print("  reward-details.json (what actually happened):")
    print()
    show_criteria(reward_details(job_dir))
    print("  This is the file that makes a failing verifier debuggable. It is")
    print("  also what `harbor view jobs` renders under Verifier Logs -> Rewards.")
    print()


def step_refactor() -> None:
    """Step 4: the bash verifier, rewritten."""
    print("=" * 60)
    print("Step 4: Rewriting Lesson 1's Verifier")
    print("=" * 60)
    print()
    print("  Lesson 1 graded a report with ~20 lines of bash: a loop, a")
    print("  counter, an awk call to compute the fraction, a redirect.")
    print()
    print("  Here is the whole thing in RewardKit:")
    print()
    checks = LESSON_DIR / "tasks" / "report-rewardkit" / "tests" / "checks.py"
    for line in checks.read_text().splitlines():
        if line.strip().startswith("rk."):
            print(f"    {line}")
    print()
    print("  Same three checks, same 0.00 / 0.33 / 0.67 / 1.00 scale --")
    print("  RewardKit does the averaging. And file_contains already returns")
    print("  False when the file is missing, so the existence check the bash")
    print("  version needed is gone too.")
    print()

    if not run_task(LESSON_DIR, "report-rewardkit"):
        print("  Trial failed. Skipping analysis.")
        return

    job_dir = latest_job_dir(LESSON_DIR)
    if job_dir is None:
        return

    show_rewards("Reward (lesson 1's bash version scored 1.00):", trial_rewards(job_dir))
    show_criteria(reward_details(job_dir))


def show_summary() -> None:
    """Print the lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("  test.sh becomes one line; the criteria become data.")
    print()
    print("  What you get that bash did not give you:")
    print("    - a per-criterion breakdown in reward-details.json")
    print("    - weights, so not every check counts the same")
    print("    - errors attributed to the criterion that raised them")
    print("    - 23 built-ins covering files, commands, JSON, CSV, HTTP, images")
    print()
    print("  What to watch for:")
    print("    - `uvx --from 'harbor-rewardkit==0.1.*' rewardkit` -- the --from")
    print("      is mandatory and the version pin keeps runs reproducible")
    print("    - criteria run CONCURRENTLY; never let one depend on another's")
    print("      side effects")
    print("    - numeric criteria are NOT clamped to 0-1")
    print("    - isolated=True needs overlayfs, which a stock Docker container")
    print("      cannot mount -- see the README before reaching for it")
    print()
    print("  Next lesson: lesson-4-judge-criteria (rubrics as TOML)")


def main() -> None:
    """Run the RewardKit basics lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 2, Module 8          #")
    print("#          Lesson 3: RewardKit Programmatic Criteria    #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_rewardkit()
    show_catalogue()
    step_wordstats()
    step_refactor()
    show_summary()


if __name__ == "__main__":
    main()
