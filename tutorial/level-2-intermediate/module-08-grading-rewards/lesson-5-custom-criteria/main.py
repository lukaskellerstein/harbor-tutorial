"""
Module 8, Lesson 5: Custom Criteria & Multi-Dimensional Rewards

Write your own criterion functions, split tests/ into named reward dimensions,
aggregate them with reward.toml -- then compare two candidate verifiers against
the same workspace to see how much the verifier itself decides the score.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from guardrails import demo_direct_call_typeerror, demo_nested_layout_valueerror
from results import (
    gateway_reachable,
    latest_job_dir,
    reward_details,
    run_task,
    show_criteria_by_dimension,
    show_dimensions,
    trial_rewards,
)

LESSON_DIR = Path(__file__).parent
TESTS = LESSON_DIR / "tasks" / "pipeline" / "tests"
LOCAL = LESSON_DIR / "local"

AGGREGATED_KEYS = {"reward", "all_dimensions_passed"}


def check_prerequisites() -> bool:
    """Verify Docker, Harbor, and the LiteLLM gateway are available."""
    print("=" * 60)
    print("Checking Prerequisites")
    print("=" * 60)

    docker_ok = shutil.which("docker") is not None
    harbor_ok = shutil.which("harbor") is not None
    docker_running = (
        subprocess.run(
            ["docker", "info"], capture_output=True, text=True, check=False
        ).returncode
        == 0
    )
    gateway_ok = gateway_reachable()

    print(f"  Docker CLI:      {'[OK]' if docker_ok else '[MISSING]'}")
    print(f"  Docker running:  {'[OK]' if docker_running else '[NOT RUNNING]'}")
    print(f"  Harbor CLI:      {'[OK]' if harbor_ok else '[MISSING]'}")
    print(f"  LiteLLM gateway: {'[OK]' if gateway_ok else '[UNREACHABLE]'}")
    print()

    if not gateway_ok:
        print("  Start it with:  cd infra && docker compose up -d litellm")
        print()

    if not (docker_ok and docker_running and harbor_ok and gateway_ok):
        print("  Prerequisites not met. Fix the issues above.")
        return False
    return True


def explain_layout() -> None:
    """Step 1: directories become dimensions."""
    print("=" * 60)
    print("Step 1: Directories Are Dimensions")
    print("=" * 60)
    print()
    print("  Every SUBDIRECTORY of tests/ becomes its own named reward.")
    print()
    print("    tests/")
    print("      test.sh")
    print("      criteria.py              shared custom criteria (not a dimension)")
    print("      reward.toml              aggregation config (not a dimension)")
    print("      correctness/functions.py -> reward \"correctness\"")
    print("      structure/files.py       -> reward \"structure\"")
    print("      quality/quality.toml     -> reward \"quality\"")
    print()
    print("  Two files at the root are NOT dimensions, for different reasons:")
    print("    criteria.py  a .py file at the root is imported for its shared")
    print("                 definitions, never registered as its own reward")
    print("    reward.toml  a .toml without [judge] is reward CONFIG, not a")
    print("                 rubric -- which is exactly why a rubric must have")
    print("                 both [judge] and [[criterion]] to count as one")
    print()
    print("  A dimension can mix kinds: drop a .py file into quality/ next to")
    print("  quality.toml and that dimension gets both a programmatic and a")
    print("  judged reward, combined by their reward_weight.")
    print()


def explain_custom_criteria() -> None:
    """Step 2: the three ways to define a criterion."""
    print("=" * 60)
    print("Step 2: Writing Your Own Criteria")
    print("=" * 60)
    print()
    print("  Three forms, and the difference matters.")
    print()
    print("  1. ZERO-PARAMETER -- defining it registers it.")
    print()
    print("     @criterion")
    print("     def top_word_correct(workspace: Path) -> bool:")
    print("         ...")
    print()
    print("  2. PARAMETERIZED -- defining it registers NOTHING. RewardKit")
    print("     cannot guess your arguments, so you must call it, and the")
    print("     description is str.format-ed with what you passed:")
    print()
    print("     @criterion(description=\"defines at least {n} public functions\")")
    print("     def defines_n_functions(workspace: Path, n: int) -> bool:")
    print("         ...")
    print()
    print("     rk.defines_n_functions(3, weight=2.0)")
    print()
    print("     Forget the call and you get:")
    print("       UserWarning: Criterion 'defines_n_functions' was defined with")
    print("       @criterion but never called.")
    print()
    print("  3. SHARED -- defined once at the root, used by any dimension:")
    print()
    print("     @criterion(shared=True)")
    print("     def word_count_correct(workspace: Path) -> float:")
    print("         ...")
    print()
    print("     from rewardkit import criteria")
    print("     criteria.word_count_correct(weight=3.0)")
    print()
    print("  Returning a float instead of a bool buys partial credit. The")
    print("  shared criteria here run the agent's OWN functions against")
    print("  held-out inputs and return the pass fraction -- which is a much")
    print("  better measurement than checking its output file, because an")
    print("  output file can be hardcoded and a function cannot.")
    print()


def step_guardrails() -> None:
    """Step 3: the two structural guardrails."""
    print("=" * 60)
    print("Step 3: Two Guardrails, Demonstrated")
    print("=" * 60)
    print()
    demo_direct_call_typeerror()
    demo_nested_layout_valueerror()


def step_run() -> None:
    """Step 4: run the multi-dimensional task."""
    print("=" * 60)
    print("Step 4: A Reward With Three Dimensions")
    print("=" * 60)
    print()
    print("  tests/reward.toml adds aggregated keys on top of the dimensions:")
    print()
    for line in (TESTS / "reward.toml").read_text().splitlines():
        if line.strip() and not line.strip().startswith("#"):
            print(f"    {line}")
    print()

    if not run_task(LESSON_DIR, "pipeline"):
        print("  Trial failed. Skipping analysis.")
        return

    job_dir = latest_job_dir(LESSON_DIR)
    if job_dir is None:
        return

    show_dimensions(trial_rewards(job_dir), AGGREGATED_KEYS)
    print("  Per criterion, grouped by dimension:")
    print()
    show_criteria_by_dimension(reward_details(job_dir))
    print("  Reporting both an aggregate and a gate means never choosing")
    print("  between \"how good was it\" and \"did it clear the bar\".")
    print()


def step_compare() -> None:
    """Step 5: compare two candidate verifiers."""
    print("=" * 60)
    print("Step 5: Which Verifier Is Better?")
    print("=" * 60)
    print()
    print("  RewardKit accepts several tests directories at once and grades the")
    print("  same workspace with each, so you can compare candidate verifiers:")
    print()
    print("    rewardkit local/v1 local/v2 --workspace local/workspace")
    print()
    print("  local/workspace holds a SUBTLY broken implementation: word_count")
    print("  splits on a literal space instead of on whitespace. The sample file")
    print("  has no double spaces, so results.json is perfect anyway.")
    print()
    print("    v1 grades the OUTPUT   -- files exist, results.json is right")
    print("    v2 grades the FUNCTION -- calls word_count() on held-out inputs")
    print()

    cmd = [
        "uvx",
        "--from",
        "harbor-rewardkit==0.1.*",
        "rewardkit",
        str(LOCAL / "v1"),
        str(LOCAL / "v2"),
        "--workspace",
        str(LOCAL / "workspace"),
        "--output",
        str(LOCAL / "reward.json"),
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(LESSON_DIR), check=False
    )
    for line in (result.stdout or "").splitlines():
        print(f"    {line}")
    for line in (result.stderr or "").splitlines():
        if "warning" not in line.lower():
            print(f"    {line}")
    print()
    print("  v1 gives the broken implementation full marks. v2 does not.")
    print("  Same agent, same workspace, different number -- because a verifier")
    print("  is a measurement instrument, and a lenient one reports a score you")
    print("  cannot trust. Compare verifiers the way you compare agents.")
    print()


def show_summary() -> None:
    """Print the lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("  Layout:")
    print("    - each tests/ subdirectory is a named reward dimension")
    print("    - root .py = shared definitions, root reward.toml = aggregation")
    print("    - [[reward]] blocks ADD keys; the dimensions stay alongside")
    print()
    print("  Custom criteria:")
    print("    - zero-parameter registers on definition; parameterized does not")
    print("    - call through the module (rk.x / criteria.x), never directly")
    print("    - shared=True is mandatory for root criteria in a nested layout")
    print("    - return a float for partial credit")
    print()
    print("  And: test the agent's functions, not just its output files.")
    print()
    print("  Next lesson: lesson-6-trajectory-judging (grading HOW the agent")
    print("  worked, and defending the verifier against the agent)")


def main() -> None:
    """Run the custom-criteria lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 2, Module 8          #")
    print("#          Lesson 5: Custom Criteria & Dimensions       #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_layout()
    explain_custom_criteria()
    step_guardrails()
    step_run()
    step_compare()
    show_summary()


if __name__ == "__main__":
    main()
