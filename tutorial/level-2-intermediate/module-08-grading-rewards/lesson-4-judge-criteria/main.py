"""
Module 8, Lesson 4: RewardKit Judge Criteria

Lesson 2's 150-line judge, rewritten as a TOML rubric with no Python at all.
Then: how the five aggregation modes turn the same criterion scores into very
different rewards, and how to swap judge models without touching a file.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from rewardkit.models import Aggregation, Score
from rewardkit.reward import aggregate_scores

from results import (
    gateway_reachable,
    judged_criteria,
    latest_job_dir,
    reward_details,
    run_task,
    show_judgement,
    show_rewards,
    trial_rewards,
)

LESSON_DIR = Path(__file__).parent
RUBRIC = LESSON_DIR / "tasks" / "poem-rubric" / "tests" / "judge.toml"

AGGREGATIONS: list[Aggregation] = [
    "weighted_mean",
    "all_pass",
    "any_pass",
    "threshold",
    "required_pass",
]


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
        print("  Start it with:  cd infra && docker compose up -d litellm")
        print()

    if not (docker_ok and docker_running and harbor_ok and gateway_ok):
        print("  Prerequisites not met. Fix the issues above.")
        return False
    return True


def explain_rubric() -> None:
    """Step 1: rubric anatomy."""
    print("=" * 60)
    print("Step 1: A Rubric Is a TOML File")
    print("=" * 60)
    print()
    print("  RewardKit treats a .toml under tests/ as a rubric if and only if")
    print("  it has BOTH a [judge] table and at least one [[criterion]].")
    print("  Anything else is ignored -- which is how tests/reward.toml")
    print("  (lesson 5) can sit in the same directory without confusing it.")
    print()
    print("  tasks/poem-rubric/tests/judge.toml:")
    print()
    for line in RUBRIC.read_text().splitlines():
        print(f"    {line}")
    print()
    print("  Three output formats, all normalised to 0.0-1.0:")
    print("    binary            yes/no        -> 1.0 / 0.0")
    print("    likert  (points)  1..N          -> (raw - 1) / (points - 1)")
    print("    numeric (min/max) a free score  -> scaled into the range")
    print()
    print("  Two flags worth knowing:")
    print("    negate = true    ask the natural question, flip the answer")
    print("    optional = true  excluded from required_pass aggregation")
    print()
    print("  And one trap: the criterion NAME is part of the judge's prompt.")
    print("  RewardKit renders each criterion as")
    print()
    print("    - 'contains_profanity': Does the poem contain profanity? (score: yes/no)")
    print()
    print('  so a name that disagrees with the description -- "no_profanity"')
    print('  paired with "does it contain profanity?" -- puts a contradiction')
    print("  in front of the judge. It answers the label, negate flips the")
    print("  already-correct answer, and a clean poem scores 0.00. Name")
    print("  criteria after the QUESTION, not after the outcome you want.")
    print()


def step_judge() -> dict | None:
    """Step 2: run the rubric for real."""
    print("=" * 60)
    print("Step 2: Judging Against the Rubric")
    print("=" * 60)
    print()

    if not run_task(LESSON_DIR, "poem-rubric"):
        print("  Trial failed. Skipping analysis.")
        return None

    job_dir = latest_job_dir(LESSON_DIR)
    if job_dir is None:
        return None

    show_rewards("reward.json:", trial_rewards(job_dir))

    details = reward_details(job_dir)
    print("  Per-criterion, from reward-details.json:")
    print()
    show_judgement(details)
    print("  Note `raw` versus `value`. Likert criteria store the 1-5 answer as")
    print("  raw and the normalised score as value; the negated criterion stores")
    print("  the judge's literal answer as raw and the flipped score as value.")
    print("  The inversion stays auditable instead of silently applied.")
    print()
    return details


def step_aggregations(details: dict | None) -> None:
    """Step 3: same scores, five aggregation modes."""
    print("=" * 60)
    print("Step 3: Aggregation Changes Everything")
    print("=" * 60)
    print()

    criteria = judged_criteria(details)
    if not criteria:
        print("  Need a completed judge run to compare. Skipping.")
        print()
        return

    # Rebuild the Score objects from what the judge actually returned, then feed
    # them through RewardKit's own aggregate_scores -- not a reimplementation.
    scores = [Score.model_validate(c) for c in criteria]

    print("  Taking the exact scores the judge just produced:")
    width = max(len(s.name) for s in scores)
    for score in scores:
        print(f"    {score.name:<{width}}  {score.value:.2f}  (weight {score.weight})")
    print()
    print("  ...and running each aggregation mode over them:")
    print()
    print(f"    {'aggregation':<16} {'reward':>7}   meaning")
    print(f"    {'-' * 16} {'-' * 7}   {'-' * 40}")

    meanings = {
        "weighted_mean": "weighted average of every criterion",
        "all_pass": "1.0 only if EVERY criterion scored > 0",
        "any_pass": "1.0 if ANY criterion scored > 0",
        "threshold": "1.0 if the weighted mean >= threshold (0.5)",
        "required_pass": "all_pass, ignoring optional=true criteria",
    }
    for mode in AGGREGATIONS:
        value = aggregate_scores(scores, mode, threshold=0.5)
        print(f"    {mode:<16} {value:>7.2f}   {meanings[mode]}")
    print()
    print("  Identical judging, very different verdicts. Choose deliberately:")
    print("    - weighted_mean for leaderboards and comparisons")
    print("    - all_pass / required_pass for gates where partial credit is a lie")
    print("    - threshold when you want a gate but tolerate an imperfect score")
    print("    - any_pass mostly for smoke tests")
    print()
    print("  Look at the gap between weighted_mean and all_pass above. They are")
    print("  scoring the same judgement and they disagree wildly, because")
    print('  all_pass asks "is every criterion > 0?" -- NOT "is every criterion')
    print('  1.0?". On graded criteria that is a very low bar: a likert answer')
    print("  of 2/5 normalises to 0.25 and sails through. all_pass only bites")
    print("  when something scores exactly 0.0, which for likert means the")
    print("  judge picked the very bottom of the scale.")
    print()
    print("  So all_pass is a strong gate over BINARY criteria and a nearly")
    print("  meaningless one over likert and numeric criteria. Mixing both in")
    print("  one rubric under all_pass mostly measures your binary criteria.")
    print()


def step_overrides() -> None:
    """Step 4: swapping judges without editing the rubric."""
    print("=" * 60)
    print("Step 4: Swapping the Judge")
    print("=" * 60)
    print()
    print("  judge.toml names a model:")
    print()
    print('    judge = "openai/gemma-large"')
    print()
    print("  RewardKit reads REWARDKIT_JUDGE first and only falls back to that")
    print("  line (rewardkit/runner.py:_build_judge_from_toml). So a rubric")
    print("  committed to your repo can be re-judged by anything:")
    print()
    print("    # for one run")
    print("    REWARDKIT_JUDGE=openai/gpt-mini uv run python main.py")
    print()
    print("    # or directly, outside Harbor")
    print("    rewardkit /tests --judge openai/gemma-local")
    print()
    print("  REWARDKIT_MODEL does the same for an agent judge's inner model.")
    print()
    print("  This matters more than it looks. Judge choice is the single")
    print("  biggest lever on your scores, and keeping it in the environment")
    print("  means you can re-grade an entire benchmark with a stronger judge")
    print("  without a single diff to the rubrics.")
    print()
    print('  Agent judges: set judge = "claude-code" (or "codex") and the')
    print("  judge gets a filesystem instead of a fixed list of files -- it can")
    print("  explore the workspace, run things, and grade what it finds:")
    print()
    print("    [judge]")
    print('    judge = "claude-code"')
    print("    isolated = true")
    print()
    print("    [[judge.mcp_servers]]")
    print('    name = "playwright"')
    print('    transport = "stdio"')
    print('    command = "npx"')
    print('    args = ["@playwright/mcp@latest", "--headless"]')
    print()
    print("  That costs real money per trial, so this lesson does not run one.")
    print()


def show_summary() -> None:
    """Print the lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("  Lesson 2's judge was 150 lines of Python. This is the same idea as")
    print("  a TOML file, with retries, concurrency, and per-criterion reporting")
    print("  handled for you.")
    print()
    print("  Rubric checklist:")
    print("    - [judge] + [[criterion]] or it is not a rubric")
    print("    - `files` decides what the judge can see; without it, nothing")
    print("    - binary / likert(points) / numeric(min,max)")
    print('    - mode = "individual" is REQUIRED if a criterion sets its own')
    print("      `files` -- batched raises ValueError")
    print("    - negate for natural-language polarity, optional for soft criteria")
    print("    - [scoring] aggregation is a real decision, not a default")
    print()
    print("  Next lesson: lesson-5-custom-criteria (your own checks, and")
    print("  splitting a reward into named dimensions)")


def main() -> None:
    """Run the judge-criteria lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 2, Module 8          #")
    print("#          Lesson 4: RewardKit Judge Criteria           #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_rubric()
    details = step_judge()
    step_aggregations(details)
    step_overrides()
    show_summary()


if __name__ == "__main__":
    main()
