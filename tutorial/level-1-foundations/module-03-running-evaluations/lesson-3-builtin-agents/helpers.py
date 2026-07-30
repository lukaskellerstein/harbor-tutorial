"""Helper functions for the built-in agents lesson."""

import subprocess


def check_prerequisites() -> bool:
    """Verify that Docker and Harbor are available."""
    print("=" * 60)
    print("Checking prerequisites")
    print("=" * 60)

    result = subprocess.run(
        ["docker", "info"], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        print("ERROR: Docker is not running. Please start Docker and try again.")
        return False
    print("[OK] Docker is running")

    result = subprocess.run(
        ["harbor", "--help"], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        print("ERROR: Harbor is not installed. Run: uv tool install harbor")
        return False
    print("[OK] Harbor is installed")
    print()
    return True


def run_harbor_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a harbor CLI command and print its output."""
    print(f"Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    return result


# Agent catalog organized by category
AGENT_CATEGORIES: list[tuple[str, list[tuple[str, str]]]] = [
    ("GENERAL-PURPOSE CODING AGENTS", [
        ("claude-code", "Anthropic's Claude Code CLI agent"),
        ("copilot-cli", "GitHub Copilot CLI agent"),
        ("cursor-cli", "Cursor editor CLI agent"),
        ("codex", "OpenAI Codex CLI agent"),
        ("gemini-cli", "Google Gemini CLI agent"),
        ("aider", "Aider -- AI pair programming in terminal"),
        ("openhands", "OpenHands (formerly OpenDevin) agent"),
        ("openhands-sdk", "OpenHands SDK-based agent"),
        ("opencode", "OpenCode CLI agent"),
        ("goose", "Block's Goose AI agent"),
        ("grok-build", "xAI Grok Build agent"),
        ("kimi-cli", "Moonshot Kimi CLI agent"),
        ("qwen-coder", "Alibaba Qwen Code agent"),
        ("trae-agent", "Trae AI agent"),
        ("rovodev-cli", "Atlassian Rovo Dev CLI agent"),
        ("devin", "Cognition Devin agent"),
        ("vibe", "Vibe coding agent"),
        ("antigravity-cli", "Antigravity CLI agent"),
        ("eve", "Eve AI agent"),
        ("pi", "Pi AI agent"),
        ("hermes", "Hermes AI agent"),
    ]),
    ("MULTI-AGENT & FRAMEWORK AGENTS", [
        ("langgraph", "LangGraph-based stateful agent"),
        ("deerflow", "DeerFlow multi-agent framework"),
        ("mimo", "MiMo agent framework"),
        ("dspy-rlm", "DSPy Reasoning Language Model agent"),
        ("nemo-agent", "NVIDIA NeMo agent"),
    ]),
    ("SPECIALIZED SWE AGENTS", [
        ("swe-agent", "Princeton SWE-agent for software engineering"),
        ("mini-swe-agent", "Lightweight SWE agent"),
        ("openclaw", "OpenClaw SWE agent"),
    ]),
    ("COMPUTER-USE AGENTS", [
        ("computer-1", "Computer-use agent (screen interaction)"),
        ("terminus-2", "Terminal-use agent v2"),
    ]),
    ("PROTOCOL-BASED AGENTS", [
        ("acp", "Agent Communication Protocol agent (acp:<name>)"),
    ]),
    ("UTILITY AGENTS", [
        ("oracle", "Runs solution/solve.sh -- validates task correctness"),
        ("nop", "Does nothing -- tests environment builds"),
    ]),
]

CLI_EXAMPLES: list[tuple[str, str, str]] = [
    ("claude-code", "anthropic/claude-sonnet-4-5-20250929", "Anthropic Claude Sonnet"),
    ("claude-code", "anthropic/claude-opus-4-1-20250620", "Anthropic Claude Opus"),
    ("codex", "openai/gpt-4o", "OpenAI GPT-4o"),
    ("gemini-cli", "gemini/gemini-2.5-pro", "Google Gemini 2.5 Pro"),
    ("aider", "anthropic/claude-sonnet-4-5-20250929", "Aider with Claude"),
    ("openhands", "anthropic/claude-sonnet-4-5-20250929", "OpenHands with Claude"),
]
