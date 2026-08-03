"""
Module 8, Lesson 2: LLM-as-a-Judge from Scratch

Grades a poem -- something no grep can score -- by handing it to a model with an
explicit rubric and a strict JSON schema. Runs the same trial twice to show how
much a judge disagrees with itself.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from results import (
    gateway_reachable,
    judge_stdout,
    latest_job_dir,
    run_task,
    show_rewards,
    trial_rewards,
)

LESSON_DIR = Path(__file__).parent
JUDGE_SCRIPT = LESSON_DIR / "tasks" / "poem-judge" / "tests" / "llm_judge.py"


def check_prerequisites() -> bool:
    """Verify Docker, Harbor, and the LiteLLM gateway are available."""
    print("=" * 60)
    print("Checking Prerequisites")
    print("=" * 60)

    docker_ok = shutil.which("docker") is not None
    harbor_ok = shutil.which("harbor") is not None
    docker_running = subprocess.run(["docker", "info"], capture_output=True, text=True, check=False).returncode == 0
    gateway_ok = gateway_reachable()

    print(f"  Docker CLI:      {'[OK]' if docker_ok else '[MISSING]'}")
    print(f"  Docker running:  {'[OK]' if docker_running else '[NOT RUNNING]'}")
    print(f"  Harbor CLI:      {'[OK]' if harbor_ok else '[MISSING]'}")
    print(f"  LiteLLM gateway: {'[OK]' if gateway_ok else '[UNREACHABLE]'}")
    print()

    if not gateway_ok:
        print("  The judge needs the LiteLLM gateway on http://localhost:4000.")
        print("  Start it with:  cd infra && docker compose up -d litellm")
        print()

    if not (docker_ok and docker_running and harbor_ok and gateway_ok):
        print("  Prerequisites not met. Fix the issues above.")
        return False
    return True


def explain_judging() -> None:
    """Step 1: when a judge is the right tool."""
    print("=" * 60)
    print("Step 1: When You Need a Judge")
    print("=" * 60)
    print()
    print("  Lesson 1 graded with grep: the section either exists or it does not.")
    print("  This task asks for a FUNNY poem. No amount of grep will score that.")
    print()
    print("  The rules that still apply:")
    print('    1. Write the rubric down. "Is it good?" is not gradable;')
    print('       "is the joke landing?" is.')
    print("    2. Run every deterministic check FIRST. Never spend an LLM call")
    print("       on a question len() can answer.")
    print("    3. Demand structured output and validate it. A model that")
    print("       returns 7.5 on a 0-1 scale must fail loudly, not inflate")
    print("       your reward.")
    print("    4. Never swallow a judge error into a 0.0 -- a broken judge and")
    print("       a bad submission would then look identical.")
    print()


def show_judge_source() -> None:
    """Step 2: walk the judge script."""
    print("=" * 60)
    print("Step 2: The Judge Script")
    print("=" * 60)
    print()
    print("  tests/llm_judge.py declares its own dependencies inline (PEP 723),")
    print("  so tests/test.sh is a single line:")
    print()
    print("    uv run /tests/llm_judge.py")
    print()
    print("  Its rubric:")
    print()

    source = JUDGE_SCRIPT.read_text()
    inside = False
    for line in source.splitlines():
        if line.startswith("RUBRIC = {"):
            inside = True
        if inside:
            print(f"    {line}")
        if inside and line.startswith("}"):
            break
    print()
    print("  It reaches the model through the LiteLLM gateway. task.toml wires")
    print("  that up without hardcoding a single credential:")
    print()
    print("    [verifier.env]")
    print('    OPENAI_BASE_URL = "${LITELLM_BASE_URL:-http://host.docker.internal:4000/v1}"')
    print('    OPENAI_API_KEY  = "${LITELLM_MASTER_KEY:-sk-litellm-master}"')
    print('    JUDGE_MODEL     = "${JUDGE_MODEL:-gemma-large}"')
    print()
    print("  host.docker.internal is the host as seen from inside the container.")
    print("  Swapping judge models is a JUDGE_MODEL change -- never a code change.")
    print()


def run_and_report(step: int, title: str) -> dict[str, float]:
    """Run the task once and print what the judge decided."""
    print("=" * 60)
    print(f"Step {step}: {title}")
    print("=" * 60)
    print()

    if not run_task(LESSON_DIR, "poem-judge"):
        print("  Trial failed. Skipping analysis.")
        return {}

    job_dir = latest_job_dir(LESSON_DIR)
    if job_dir is None:
        return {}

    rewards = trial_rewards(job_dir)
    show_rewards("Rewards recorded on the trial:", rewards)

    print("  What the judge printed (captured at verifier/test-stdout.txt):")
    for line in judge_stdout(job_dir).splitlines():
        if line.strip():
            print(f"    {line}")
    print()
    return rewards


def compare_runs(first: dict[str, float], second: dict[str, float]) -> None:
    """Step 5: judge non-determinism."""
    print("=" * 60)
    print("Step 5: Judges Disagree With Themselves")
    print("=" * 60)
    print()

    if not first or not second:
        print("  Need two successful runs to compare. Skipping.")
        print()
        return

    print(f"  {'dimension':<12} {'run 1':>7} {'run 2':>7} {'delta':>7}")
    print(f"  {'-' * 12} {'-' * 7} {'-' * 7} {'-' * 7}")
    for key, value in first.items():
        a, b = float(value), float(second.get(key, 0.0))
        print(f"  {key:<12} {a:>7.2f} {b:>7.2f} {b - a:>+7.2f}")
    print()

    drift = max(abs(float(second.get(k, 0)) - float(v)) for k, v in first.items())
    if drift == 0:
        print("  Identical this time -- but that is luck, not a guarantee.")
    else:
        print(f"  Same poem, same rubric, scores moved by up to {drift:.2f}.")
    print()
    print("  This is why judged dimensions are not pass/fail gates. Compare")
    print("  agents against each other on the same rubric, average over several")
    print("  trials, and keep the hard gates on deterministic checks.")
    print()


def show_summary() -> None:
    """Print the lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("  A judge is just a verifier that happens to call a model:")
    print("    - explicit rubric, one criterion at a time")
    print("    - deterministic checks first, LLM only for the rest")
    print("    - strict JSON schema in, validated object out")
    print("    - errors raised, never scored as 0.0")
    print("    - credentials via [verifier.env], never in the repo")
    print()
    print("  You now maintain ~150 lines of judge for two criteria. The next")
    print("  lesson replaces the whole thing with declarative criteria files.")
    print()
    print("  Next lesson: lesson-3-rewardkit-basics")


def main() -> None:
    """Run the LLM-as-a-judge lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 2, Module 8          #")
    print("#          Lesson 2: LLM-as-a-Judge from Scratch        #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_judging()
    show_judge_source()
    first = run_and_report(3, "Judging a Poem")
    second = run_and_report(4, "Judging the Same Poem Again")
    compare_runs(first, second)
    show_summary()


if __name__ == "__main__":
    main()
