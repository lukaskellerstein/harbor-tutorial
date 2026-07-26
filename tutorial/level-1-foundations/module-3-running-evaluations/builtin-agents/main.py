"""
Lesson: Built-in Agents
=======================
Survey Harbor's 37+ built-in agents, understand categories, and see
how to run evaluations with different agents and models.
"""

import sys

from helpers import (
    AGENT_CATEGORIES,
    CLI_EXAMPLES,
    check_prerequisites,
    run_harbor_command,
)


def list_builtin_agents() -> None:
    """Display all built-in agents organized by category."""
    print("=" * 60)
    print("Step 1: Harbor's built-in agents")
    print("=" * 60)
    print("\nHarbor ships with 37+ built-in agents. Specify them by name")
    print("using the -a flag: harbor run -a <agent-name>\n")

    for category_name, agents in AGENT_CATEGORIES:
        print("-" * 60)
        print(category_name)
        print("-" * 60)
        for name, desc in agents:
            print(f"  {name:<22} {desc}")
        print()


def show_agent_cli_syntax() -> None:
    """Show how to use agents via CLI with model specification."""
    print("=" * 60)
    print("Step 2: Using agents via the CLI")
    print("=" * 60)
    print("\nBasic syntax:")
    print("  harbor run -p <tasks> -a <agent-name> -m <model> --delete\n")
    print("The model name follows LiteLLM convention: <provider>/<model-id>\n")

    for agent, model, description in CLI_EXAMPLES:
        print(f"  # {description}")
        print(f"  harbor run -p tasks -a {agent} -m {model} --delete\n")

    print("Each agent requires API keys for its model provider.")
    print("Set them as env vars (ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.)\n")


def show_multi_agent_job() -> None:
    """Show how to compare multiple agents in a single job.yaml."""
    print("=" * 60)
    print("Step 3: Comparing agents in a single job")
    print("=" * 60)
    print("\nEvaluate multiple agents in one job.yaml:\n")
    print("  agents:")
    print("    - name: claude-code")
    print("      model_name: anthropic/claude-sonnet-4-5-20250929")
    print("    - name: codex")
    print("      model_name: openai/gpt-4o\n")
    print("Harbor creates a trial for every (agent, task) combination.")
    print("With 3 agents and 10 tasks, you get 30 trials.\n")
    print("Or use repeated -m flags on the CLI:\n")
    print("  harbor run -p tasks -a claude-code \\")
    print("    -m anthropic/claude-sonnet-4-5-20250929 \\")
    print("    -m anthropic/claude-opus-4-1-20250620 --delete\n")


def run_demo_trial() -> None:
    """Run a quick evaluation with the oracle agent."""
    print("=" * 60)
    print("Step 4: Demo -- running with the oracle agent")
    print("=" * 60)
    print("\nThe oracle requires no API keys, so we use it for the demo.\n")
    print("Running...")
    print("-" * 60)

    cmd = [
        "harbor", "trial", "start",
        "-p", "tasks/hello-task", "-a", "oracle", "--delete",
    ]

    result = run_harbor_command(cmd)

    print("-" * 60)
    if result.returncode == 0:
        print("\nThe oracle confirmed the task's solution is correct.\n")
    else:
        print(f"\nTrial failed with exit code {result.returncode}\n")


def explain_custom_agents() -> None:
    """Mention that custom agents are also possible."""
    print("=" * 60)
    print("Step 5: Beyond built-in agents")
    print("=" * 60)
    print("\nHarbor also supports:\n")
    print("  Custom external agents (BaseAgent):")
    print("    harbor run -p tasks -a my_module:MyAgent\n")
    print("  Custom installed agents (BaseInstalledAgent):")
    print("    Agents that install themselves inside the container.\n")
    print("  ACP agents:")
    print("    harbor run -p tasks -a acp:agent-name@version\n")
    print("Custom agents are covered in Module 4.\n")


def recap() -> None:
    """Summarize what was learned."""
    print("=" * 60)
    print("Recap")
    print("=" * 60)
    print("\nIn this lesson you learned:\n")
    print("  1. Harbor has 37+ built-in agents across multiple categories")
    print("  2. Use -a <agent-name> to select an agent")
    print("  3. Use -m <provider>/<model> for the model (LiteLLM format)")
    print("  4. Multiple agents and models can be compared in a single job")
    print("  5. Custom agents can be specified by import path")
    print("\nNext lesson: Oracle & Nop Agents\n")


def main() -> None:
    """Run the built-in agents lesson."""
    print()
    print("=" * 60)
    print("  Harbor Tutorial - Module 3, Lesson 3")
    print("  Built-in Agents")
    print("=" * 60)
    print()

    if not check_prerequisites():
        sys.exit(1)

    list_builtin_agents()
    show_agent_cli_syntax()
    show_multi_agent_job()
    run_demo_trial()
    explain_custom_agents()
    recap()


if __name__ == "__main__":
    main()
