"""
Lesson 3: Model Selection & LiteLLM — Harbor's model routing
via LiteLLM naming, CLI and job.yaml configuration, LMStudio.
"""

import shutil
import subprocess
import sys
from pathlib import Path

LESSON_DIR = Path(__file__).parent
TASK_DIR = LESSON_DIR / "tasks" / "model-test"
JOB_FILE = LESSON_DIR / "job.yaml"


def check_prerequisites() -> bool:
    """Verify Docker and Harbor are available."""
    print("=" * 60)
    print("Checking Prerequisites")
    print("=" * 60)
    docker_ok = shutil.which("docker") is not None
    harbor_ok = shutil.which("harbor") is not None
    if docker_ok:
        docker_ok = (
            subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                check=False,
            ).returncode
            == 0
        )
    print(f"  Docker: {'[OK]' if docker_ok else '[FAIL] not running'}")
    print(f"  Harbor: {'[OK]' if harbor_ok else '[FAIL] not found'}")
    print()
    return docker_ok and harbor_ok


def explain_litellm_format() -> None:
    """Explain the LiteLLM model naming convention."""
    print("=" * 60)
    print("Step 1: LiteLLM Model Format")
    print("=" * 60)
    print()
    print("  Harbor uses the LiteLLM convention:  provider/model-name")
    print()
    print(f"  {'Provider':<14} {'Model':<40} {'API'}")
    print(f"  {'-' * 14} {'-' * 40} {'-' * 16}")
    models = [
        ("anthropic/", "claude-sonnet-4-5-20250929", "Anthropic"),
        ("anthropic/", "claude-opus-4-1", "Anthropic"),
        ("openai/", "gpt-4o", "OpenAI"),
        ("openai/", "gpt-4o-mini", "OpenAI"),
        ("openai/", "gemma4-e4b", "Local (LMStudio)"),
    ]
    for provider, model, api in models:
        print(f"  {provider:<14} {model:<40} {api}")
    print()
    print("  The openai/ prefix with a custom base URL routes to any")
    print("  OpenAI-compatible API (LMStudio, Ollama, vLLM, etc.).")
    print()


def explain_cli_usage() -> None:
    """Show how to specify models on the CLI."""
    print("=" * 60)
    print("Step 2: Using the -m Flag")
    print("=" * 60)
    print()
    print("  # Anthropic model")
    print("  harbor run -p tasks/model-test -a claude-code \\")
    print("      -m anthropic/claude-sonnet-4-5-20250929")
    print()
    print("  # OpenAI model")
    print("  harbor run -p tasks/model-test -a claude-code \\")
    print("      -m openai/gpt-4o")
    print()
    print("  # Local model via LMStudio")
    print("  harbor run -p tasks/model-test -a claude-code \\")
    print("      -m openai/gemma4-e4b \\")
    print("      --agent-env OPENAI_BASE_URL=http://host.docker.internal:1234/v1 \\")
    print("      --agent-env OPENAI_API_KEY=lm-studio")
    print()


def explain_job_yaml() -> None:
    """Show how to configure models in job.yaml."""
    print("=" * 60)
    print("Step 3: Model Configuration in job.yaml")
    print("=" * 60)
    print()
    if JOB_FILE.exists():
        for line in JOB_FILE.read_text().strip().splitlines():
            print(f"    {line}")
    print()
    print("  Each agent+model combo creates a separate trial for comparison.")
    print()


def explain_lmstudio() -> None:
    """Explain LMStudio for local model serving."""
    print("=" * 60)
    print("Step 4: Local Models with LMStudio")
    print("=" * 60)
    print()
    print("  Setup:")
    print("    1. Install LMStudio (https://lmstudio.ai)")
    print("    2. Download a model (e.g., Gemma4-E4B)")
    print("    3. Start the server:  lms server start")
    print()
    print("  Server runs at http://localhost:1234/v1")
    print("  From Docker containers, use http://host.docker.internal:1234/v1")
    print()
    lms_available = shutil.which("lms") is not None
    if lms_available:
        print("  LMStudio CLI detected on this system!")
        result = subprocess.run(
            ["lms", "status"],
            capture_output=True,
            text=True,
            check=False,
        )
        status = result.stdout.strip() if result.returncode == 0 else "not running"
        print(f"  Status: {status}")
    else:
        print("  LMStudio CLI not found. Install from https://lmstudio.ai")
    print()


def explain_agent_env() -> None:
    """Explain --agent-env for passing config to agents."""
    print("=" * 60)
    print("Step 5: Passing Configuration with --agent-env")
    print("=" * 60)
    print()
    print(f"  {'Variable':<24} {'Purpose'}")
    print(f"  {'-' * 24} {'-' * 36}")
    print(f"  {'OPENAI_BASE_URL':<24} Override the OpenAI API endpoint")
    print(f"  {'OPENAI_API_KEY':<24} OpenAI (or compatible) API key")
    print(f"  {'ANTHROPIC_API_KEY':<24} Anthropic API key")
    print()
    print("  In job.yaml, use the env key under each agent:")
    print("    env:")
    print('      OPENAI_BASE_URL: "http://host.docker.internal:1234/v1"')
    print()


def run_task_validation() -> None:
    """Validate the task with the oracle agent."""
    print("=" * 60)
    print("Step 6: Validating the Test Task")
    print("=" * 60)
    print()
    print(f"  Running: harbor run -p {TASK_DIR} -a oracle")
    print()
    result = subprocess.run(
        ["harbor", "run", "-p", str(TASK_DIR), "-a", "oracle"],
        capture_output=True,
        text=True,
        cwd=str(LESSON_DIR),
        check=False,
    )
    if result.stdout:
        for line in result.stdout.strip().splitlines():
            print(f"  {line}")
    if result.stderr:
        for line in result.stderr.strip().splitlines()[-5:]:
            print(f"  [stderr] {line}")
    status = "[OK]" if result.returncode == 0 else f"[FAIL] rc={result.returncode}"
    print(f"\n  {status} Task validated")
    print()


def show_summary() -> None:
    """Display key takeaways."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("  - Format: provider/model-name (e.g. anthropic/claude-opus-4-1)")
    print("  - CLI: -m anthropic/claude-sonnet-4-5-20250929")
    print("  - job.yaml: define multiple agent+model combos for comparison")
    print("  - Local models: openai/ prefix + OPENAI_BASE_URL for LMStudio")
    print("  - host.docker.internal bridges container to host network")
    print("  - --agent-env passes API keys and endpoints to the agent")
    print()
    print("Next module: Module 8 — Grading & Rewards")


def main() -> None:
    """Run the model-routing lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 2, Module 7          #")
    print("#          Lesson 3: Model Selection & LiteLLM          #")
    print("########################################################")
    print()
    if not check_prerequisites():
        sys.exit(1)
    explain_litellm_format()
    explain_cli_usage()
    explain_job_yaml()
    explain_lmstudio()
    explain_agent_env()
    run_task_validation()
    show_summary()


if __name__ == "__main__":
    main()
