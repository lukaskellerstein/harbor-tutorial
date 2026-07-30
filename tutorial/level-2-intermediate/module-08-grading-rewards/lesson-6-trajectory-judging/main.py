"""
Module 8, Lesson 6: Judging the Process, Not Just the Output

Two halves. First: grade HOW the agent worked, using its ATIF trajectory.
Second: notice that the agent can write to the same filesystem as the verifier,
and do something about it.
"""

import shutil
import subprocess
import sys
from pathlib import Path

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
AGGREGATED_KEYS = {"reward"}


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


def explain_trajectories() -> None:
    """Step 1: what a trajectory is and where it lives."""
    print("=" * 60)
    print("Step 1: The Trajectory Is Evidence")
    print("=" * 60)
    print()
    print("  Every grading technique so far looked at the workspace the agent")
    print("  left behind. None of them can tell these two apart:")
    print()
    print("    A: wrote sort_numbers.py, ran it, checked the output")
    print("    B: read the eight numbers and typed them out in order")
    print()
    print("  Both leave an identical, correct sorted.txt. Only one of them")
    print("  solved the task. The difference is in the trajectory.")
    print()
    print("  Harbor agents write ATIF to /logs/agent/trajectory.json:")
    print()
    print("    {\"schema_version\": \"ATIF-v1.7\",")
    print("     \"agent\": {\"name\": \"claude-code\", ...},")
    print("     \"steps\": [{\"step_id\": 2, \"source\": \"agent\",")
    print("                \"tool_calls\": [{\"function_name\": \"Write\", ...}]}]}")
    print()
    print("  !! PATH GOTCHA !!")
    print("  The trajectory_* criteria default to path=\"/logs/trajectory.json\".")
    print("  Harbor writes /logs/agent/trajectory.json. The default is wrong for")
    print("  every Harbor task, and it fails SILENTLY -- a missing file loads as")
    print("  None and the criterion scores 0 with no error. Your whole process")
    print("  dimension reads zero and looks like a badly behaved agent.")
    print()
    print("  Always pass path= explicitly:")
    print()
    print('    rk.trajectory_tool_used("Write", path="/logs/agent/trajectory.json")')
    print()


def step_trajectory() -> None:
    """Step 2: grade the process."""
    print("=" * 60)
    print("Step 2: Grading the Process")
    print("=" * 60)
    print()
    print("  Three dimensions over the same trial:")
    print("    outcome/    is sorted.txt right?          (workspace)")
    print("    process/    did it write and run code?    (trajectory criteria)")
    print("    approach/   was the method sound?         (judge)")
    print()
    print("  A rubric can also hand the trajectory to the judge:")
    print()
    print('    atif-trajectory = "/logs/agent/trajectory.json"')
    print()
    print("  Note the HYPHEN -- an underscore is silently ignored and the judge")
    print("  just never sees it. Supplying it switches RewardKit's system prompt")
    print("  to prompts/llm_trajectory.md, so the judge grades reasoning too.")
    print()
    print("  It is commented out in this rubric, for a reason worth knowing.")
    print("  To budget how much trajectory fits in context, RewardKit calls")
    print("  litellm.get_model_info(judge.model) -- which looks the model up in")
    print("  litellm's built-in map. A GATEWAY ALIAS is not in that map, so the")
    print("  whole dimension dies:")
    print()
    print("    Exception: This model isn't mapped yet.")
    print("    model=openai/gemma-large, custom_llm_provider=openai")
    print()
    print("  Trajectory-aware JUDGING therefore needs a judge model litellm")
    print("  recognises by name -- judge that dimension directly against a")
    print("  provider rather than through the gateway. The programmatic")
    print("  trajectory criteria in process/ are unaffected.")
    print()
    print("  This task runs with `oracle`, which produces no trajectory, so")
    print("  solve.sh stages a RECORDED one at /logs/agent/trajectory.json.")
    print("  Re-run with `-a claude-code` and the trajectory is genuinely the")
    print("  agent's own.")
    print()

    if not run_task(LESSON_DIR, "trajectory-graded"):
        print("  Trial failed. Skipping analysis.")
        return

    job_dir = latest_job_dir(LESSON_DIR)
    if job_dir is None:
        return

    show_dimensions(trial_rewards(job_dir), AGGREGATED_KEYS)
    print("  Per criterion, grouped by dimension:")
    print()
    show_criteria_by_dimension(reward_details(job_dir))


def step_reward_hacking() -> dict[str, float]:
    """Step 3: the attack."""
    print("=" * 60)
    print("Step 3: The Agent Can Write to /logs/verifier")
    print("=" * 60)
    print()
    print("  By default the verifier runs INSIDE the agent's container, on the")
    print("  filesystem the agent just had write access to. Including the")
    print("  directory it is about to read its verdict from.")
    print()
    print("  tasks/reward-hacking has a \"solution\" that never sorts anything:")
    print()
    print("    mkdir -p /logs/verifier")
    print("    echo '{\"reward\": 1.0}' > /logs/verifier/reward.json")
    print()
    print("  Its verifier is honest and writes reward.txt. But lesson 1's")
    print("  precedence rule says Harbor reads reward.json FIRST -- so the")
    print("  planted file outranks the verifier's real verdict.")
    print()

    if not run_task(LESSON_DIR, "reward-hacking"):
        print("  Trial failed. Skipping analysis.")
        return {}

    job_dir = latest_job_dir(LESSON_DIR)
    if job_dir is None:
        return {}

    rewards = trial_rewards(job_dir)
    print(f"  Reward Harbor recorded: {rewards}")
    print()
    if rewards and float(rewards.get("reward", 0)) >= 1.0:
        print("  1.00. The agent did no work at all.")
        print("  The verifier's own stdout says the trial failed -- and was")
        print("  overruled by a file the agent wrote.")
    else:
        print("  The attack did not land here; check the verifier stdout.")
    print()
    return rewards


def step_hardened(hacked: dict[str, float]) -> None:
    """Step 4: the fix."""
    print("=" * 60)
    print("Step 4: Hardening the Verifier")
    print("=" * 60)
    print()
    print("  DEFENCE 1 -- clear the reward directory before writing to it.")
    print("  One line, works everywhere:")
    print()
    print("    mkdir -p /logs/verifier")
    print("    rm -f /logs/verifier/reward.json /logs/verifier/reward.txt")
    print()
    print("  Anything already in /logs/verifier is untrusted input. Deleting")
    print("  it first means the verifier's verdict is the only verdict.")
    print()
    print("  tasks/reward-hardened has the SAME cheating solve.sh and the same")
    print("  honest verifier, plus that one line:")
    print()

    if not run_task(LESSON_DIR, "reward-hardened"):
        print("  Trial failed. Skipping analysis.")
        return

    job_dir = latest_job_dir(LESSON_DIR)
    if job_dir is None:
        return

    rewards = trial_rewards(job_dir)
    hacked_value = float(hacked.get("reward", 0)) if hacked else 0.0
    hardened_value = float(rewards.get("reward", 0)) if rewards else 0.0

    print(f"  reward-hacking  -> {hacked_value:.2f}")
    print(f"  reward-hardened -> {hardened_value:.2f}")
    print()
    print("  Same agent, same cheat, same test. One line of the verifier.")
    print()
    print("  DEFENCE 2 -- give the verifier its own container:")
    print()
    print("    [verifier]")
    print('    environment_mode = "separate"')
    print()
    print("    [verifier.environment]")
    print('    docker_image = "python:3.13-slim"')
    print('    network_mode = "public"   # judges need to reach their API')
    print()
    print("  In separate mode Harbor calls empty_dirs([verifier_dir]) before")
    print("  verifying (src/harbor/trial/trial.py), so planted reward files are")
    print("  wiped whether or not your test.sh remembers to. The verifier also")
    print("  runs on a filesystem the agent never touched, so it cannot be")
    print("  sabotaged through installed packages or shadowed binaries either.")
    print()
    print("  The cost: the verifier no longer shares the agent's workspace, so")
    print("  you must declare `artifacts` for whatever it needs to see. That is")
    print("  a real design change, which is why defence 1 is worth doing even")
    print("  when you also do this.")
    print()
    print("  DEFENCE 3 -- go looking for it. `harbor analyze` ships a")
    print("  reward_hacking rubric criterion whose guidance explicitly hunts")
    print("  for agents writing to /logs/verifier/reward.txt or reward.json:")
    print()
    print("    harbor analyze jobs/<job-dir> --failing")
    print()
    print("  Covered in Module 11, Lesson 4.")
    print()


def show_summary() -> None:
    """Print the lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("  Grading the process:")
    print("    - trajectory_tool_used / _not_used / _turn_count")
    print("    - ALWAYS pass path=\"/logs/agent/trajectory.json\"; the default")
    print("      is wrong for Harbor and fails silently")
    print("    - atif-trajectory in a rubric (hyphen!) gives the judge the")
    print("      agent's reasoning as well as its output")
    print()
    print("  Defending the verifier:")
    print("    - the agent can write to /logs/verifier in the default mode")
    print("    - rm -f the reward files before writing yours")
    print("    - environment_mode = \"separate\" makes that structural")
    print("    - harbor analyze --failing hunts for it after the fact")
    print()
    print("  You have finished Module 8: Grading & Rewards.")
    print("  Next module: Module 9 -- Adapters")


def main() -> None:
    """Run the trajectory-judging lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 2, Module 8          #")
    print("#          Lesson 6: Judging the Process                #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_trajectories()
    step_trajectory()
    hacked = step_reward_hacking()
    step_hardened(hacked)
    show_summary()


if __name__ == "__main__":
    main()
