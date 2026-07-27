"""
Lesson 1: Evaluating Claude Code

Part A runs the built-in claude-code agent with no configuration at all.
Part B runs it against a task that ships its own project-scoped Claude Code
setup -- skills, a subagent, an MCP server, CLAUDE.md, and hooks.
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv


LESSON_DIR = Path(__file__).parent

# Credentials live in this lesson's .env file (git-ignored), not in the global
# shell profile. load_dotenv understands the `export KEY=value` syntax used
# there, and puts the token in os.environ so the harbor subprocess inherits it.
load_dotenv(LESSON_DIR / ".env")

# Each file under the configured task's environment/, and what it configures.
CONFIG_FILES = [
    ("claude/settings.json", "hooks + enableAllProjectMcpServers -> /app/.claude/"),
    ("claude/skills/harbor-report/SKILL.md", "a skill: the report format"),
    ("claude/agents/fact-checker.md", "a subagent, with its own context + tools"),
    ("CLAUDE.md", "project memory -> /app/CLAUDE.md"),
    ("mcp.json", "MCP server registration -> /app/.mcp.json"),
    ("mcp_server/harbor_demo.py", "the stdio MCP server itself"),
]


def check_prerequisites() -> bool:
    """Verify Docker, Harbor CLI, and Anthropic credentials are available."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
    print("=" * 60)

    ok = True

    if shutil.which("docker") and subprocess.run(
        ["docker", "info"], capture_output=True
    ).returncode == 0:
        print("  [OK] Docker is running")
    else:
        print("  [FAIL] Docker is not available or its daemon is not running")
        ok = False

    if shutil.which("harbor"):
        print("  [OK] Harbor CLI is installed")
    else:
        print("  [FAIL] Harbor CLI not found. Install with: uv tool install harbor")
        ok = False

    # Subscription token (preferred) or API key.
    if os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        print("  [OK] CLAUDE_CODE_OAUTH_TOKEN loaded (Claude subscription auth)")
        if os.environ.get("ANTHROPIC_API_KEY"):
            print("       ANTHROPIC_API_KEY is also set; CLAUDE_FORCE_OAUTH=1 will")
            print("       be passed to Harbor so the subscription token wins.")
    elif os.environ.get("ANTHROPIC_API_KEY"):
        print("  [OK] ANTHROPIC_API_KEY is set (API billing)")
        print("       To bill your subscription instead, run `claude setup-token`")
        print("       and put CLAUDE_CODE_OAUTH_TOKEN in .env")
    else:
        print("  [FAIL] No Anthropic credentials found")
        print(f"         Expected a .env file at: {LESSON_DIR / '.env'}")
        print("         Subscription: claude setup-token, then add to .env:")
        print("           export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...")
        print("         API key alternative:")
        print("           export ANTHROPIC_API_KEY=sk-ant-...")
        ok = False

    print()
    return ok


def show_tasks(tasks_dir: Path) -> None:
    """Display the instructions of every task in a dataset directory."""
    for task_dir in sorted(p for p in tasks_dir.iterdir() if p.is_dir()):
        instruction_file = task_dir / "instruction.md"
        if instruction_file.exists():
            print(f"  Task: {task_dir.name}")
            for line in instruction_file.read_text().strip().split("\n"):
                print(f"    {line}")
            print()


def show_claude_config() -> None:
    """Show the Claude Code configuration baked into the configured task."""
    print("=" * 60)
    print("Step 4: The Project-Scoped Claude Code Setup")
    print("=" * 60)
    print()
    print("  Harbor configures skills and MCP servers for you, but has no hook")
    print("  for subagents, settings.json, or hooks. So this task ships all of")
    print("  it as plain files, baked into the image at project scope:")
    print()

    env_dir = LESSON_DIR / "tasks-configured" / "claude-setup" / "environment"
    for relative_path, purpose in CONFIG_FILES:
        marker = "x" if (env_dir / relative_path).exists() else "!"
        print(f"  [{marker}] {relative_path:<38} {purpose}")

    print()
    print("  job-configured.yaml adds nothing for any of this -- no skills, no")
    print("  mcp_servers, no agent kwargs. /app is the container WORKDIR, so")
    print("  Claude Code finds all of it the same way it would on your machine.")
    print()


def run_evaluation(config_name: str, heading: str) -> None:
    """Run one Harbor job config and stream its output."""
    print("=" * 60)
    print(heading)
    print("=" * 60)
    print()
    print(f"Running: harbor run -c {config_name}")
    print("-" * 60)

    env = {**os.environ}
    if env.get("CLAUDE_CODE_OAUTH_TOKEN"):
        # Harbor's claude-code agent injects CLAUDE_CODE_OAUTH_TOKEN into the
        # container by itself; CLAUDE_FORCE_OAUTH drops any API key so the CLI
        # bills the Claude subscription instead of the API.
        env.setdefault("CLAUDE_FORCE_OAUTH", "1")

    result = subprocess.run(
        ["harbor", "run", "-c", config_name],
        capture_output=True,
        text=True,
        cwd=str(LESSON_DIR),
        env=env,
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    print("-" * 60)
    if result.returncode == 0:
        print("Evaluation completed successfully!\n")
    else:
        print(f"Evaluation exited with code {result.returncode}\n")


def inspect_results() -> None:
    """Report rewards, failures, and verifier assertions for the latest job."""
    jobs_dir = LESSON_DIR / "jobs"
    job_dirs = sorted(
        (p for p in jobs_dir.iterdir() if p.is_dir()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    ) if jobs_dir.exists() else []

    if not job_dirs:
        print("  No job results found. The evaluation may not have run.\n")
        return

    latest_job = job_dirs[0]
    print(f"  Latest job: {latest_job.name}\n")

    rewards: list[tuple[str, float]] = []
    # One result.json per trial, plus a job-level summary at the job root.
    # Only per-trial files carry "task_name", so that key also filters out
    # the job-level file (which has no task and no reward).
    for result_file in sorted(latest_job.rglob("result.json")):
        try:
            data = json.loads(result_file.read_text())
        except json.JSONDecodeError as exc:
            print(f"  Error reading {result_file}: {exc}")
            continue

        task_name = data.get("task_name")
        if task_name is None:
            continue

        trial_dir = result_file.parent
        print(f"  Task: {task_name}")

        exception_info = data.get("exception_info")
        if exception_info:
            # The trial never reached the verifier -- this is the failure
            # message you actually need, so print it instead of a bare 0.0.
            print(f"    FAILED: {exception_info.get('exception_type')}")
            print(f"    {exception_info.get('exception_message')}")
            print(f"    Full traceback: {trial_dir / 'exception.txt'}")
            print(f"    Trial log:      {trial_dir / 'trial.log'}")
        else:
            # Reward lives under verifier_result.rewards.reward, and is absent
            # entirely when the trial raised before verification. Both levels
            # can be present-but-null, so `or {}` rather than a .get default.
            verifier_result = data.get("verifier_result") or {}
            reward = (verifier_result.get("rewards") or {}).get("reward")
            reward = 0.0 if reward is None else reward
            rewards.append((task_name, reward))
            print(f"    Reward: {reward}")
            show_verifier_assertions(trial_dir)
            if reward < 1.0:
                print(f"    Verifier output:  {trial_dir / 'verifier' / 'test-stdout.txt'}")
                print(f"    Agent transcript: {trial_dir / 'agent' / 'claude-code.txt'}")

        started, finished = data.get("started_at"), data.get("finished_at")
        if started and finished:
            elapsed = datetime.fromisoformat(finished) - datetime.fromisoformat(started)
            print(f"    Duration: {elapsed.total_seconds():.1f}s")
        print()

    if rewards:
        average = sum(r for _, r in rewards) / len(rewards)
        print(f"  Average reward: {average:.2f}")
        print(f"  Tasks passed: {sum(1 for _, r in rewards if r >= 1.0)}/{len(rewards)}")
    print()


def show_verifier_assertions(trial_dir: Path) -> None:
    """Echo the verifier's PASS/FAIL lines, which name each config surface."""
    stdout_file = trial_dir / "verifier" / "test-stdout.txt"
    if not stdout_file.exists():
        return
    for line in stdout_file.read_text().splitlines():
        if line.startswith(("PASS:", "FAIL:")):
            print(f"      {line}")


def show_summary() -> None:
    """Display a summary of what was learned."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("In this lesson you learned:")
    print("  - Claude Code is a built-in Harbor agent (no wrapping needed)")
    print("  - How auth is injected into the container by the agent at runtime")
    print("  - Which parts of Claude Code Harbor configures for you (skills,")
    print("    MCP servers, permissions) and which it does not (subagents,")
    print("    settings.json, hooks, plugins)")
    print("  - How to ship all of them yourself as project-scoped files")
    print("  - Why CLAUDE_CONFIG_DIR decides whether that configuration loads")
    print("  - How to inspect results and trajectories in jobs/")
    print()
    print("Next lesson: lesson-2-langchain-agent (wrapping Langchain agents)")


def main() -> None:
    """Run the claude-code-eval lesson."""
    print()
    print("########################################################")
    print("#  HARBOR TUTORIAL - Level 2, Module 5, Lesson 1       #")
    print("#  Evaluating Claude Code                              #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    print("=" * 60)
    print("Step 2: Tasks Overview (unconfigured)")
    print("=" * 60)
    print()
    print("  Claude Code is one of Harbor's 37+ built-in agents: you reference")
    print("  it by name (-a claude-code) and write no wrapper code at all.")
    print()
    show_tasks(LESSON_DIR / "tasks")

    run_evaluation("job.yaml", "Step 3: Running Claude Code With No Configuration")
    inspect_results()

    show_claude_config()
    show_tasks(LESSON_DIR / "tasks-configured")

    run_evaluation(
        "job-configured.yaml", "Step 5: Running Claude Code With Project Config"
    )
    inspect_results()

    show_summary()


if __name__ == "__main__":
    main()
