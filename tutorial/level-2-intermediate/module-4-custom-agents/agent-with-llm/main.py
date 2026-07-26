"""
Lesson 4: LLM-Powered Custom Agent

Learn how to build a custom Harbor agent that uses a language model
to reason about tasks and generate solutions.
"""

import os
import subprocess
import sys
from pathlib import Path


def show_concept() -> None:
    """Explain the LLM-powered agent concept."""
    print("=" * 60)
    print("Step 1: The Agent-LLM-Environment Loop")
    print("=" * 60)
    print()
    print("  Custom agents can integrate LLMs for reasoning about tasks.")
    print("  Instead of hard-coding solutions, the agent asks an LLM to")
    print("  generate commands, then executes them in the container.")
    print()
    print("  Key concepts:")
    print("  - self.model_name: receives the -m flag from the CLI")
    print("  - LiteLLM: unified interface to all model providers")
    print("    (anthropic/claude-*, openai/gpt-*, etc.)")
    print("  - Iterative refinement: ask -> execute -> check -> retry")
    print()


def show_loop_diagram() -> None:
    """Display the agent-LLM-environment loop diagram."""
    print("=" * 60)
    print("Step 2: The Loop Pattern")
    print("=" * 60)
    print()
    print("    Agent                    LLM                  Container")
    print("      |                       |                       |")
    print("      |--- instruction ------>|                       |")
    print("      |<-- bash commands -----|                       |")
    print("      |                       |                       |")
    print("      |--- exec commands ---------------------------->|")
    print("      |<-- result (stdout/stderr) -------------------|")
    print("      |                       |                       |")
    print("      |   [if error]          |                       |")
    print("      |--- error + context -->|                       |")
    print("      |<-- fixed commands ----|                       |")
    print("      |--- exec commands ---------------------------->|")
    print("      |<-- result -----------------------------------|")
    print("      |                       |                       |")
    print()
    print("  The loop repeats up to 3 times until success or max retries.")
    print()


def show_agent_code() -> None:
    """Display the agent implementation."""
    print("=" * 60)
    print("Step 3: The LLM Agent Code")
    print("=" * 60)

    agent_path = Path(__file__).parent / "agent.py"
    if agent_path.exists():
        content = agent_path.read_text()
        print(f"\n  File: agent.py\n")
        for line in content.splitlines():
            print(f"    {line}")
    print()


def show_task() -> None:
    """Show the task that the agent will solve."""
    print("=" * 60)
    print("Step 4: The Task")
    print("=" * 60)

    instruction_path = (
        Path(__file__).parent / "tasks" / "llm-task" / "instruction.md"
    )
    if instruction_path.exists():
        content = instruction_path.read_text()
        print(f"\n  File: tasks/llm-task/instruction.md\n")
        for line in content.splitlines():
            print(f"    {line}")
    print()


def explain_running() -> None:
    """Explain how to run the agent with different models."""
    print("=" * 60)
    print("Step 5: Running the LLM Agent")
    print("=" * 60)
    print()
    print("  Command:")
    print("    harbor run -p tasks/llm-task \\")
    print("      --agent agent:LLMAgent \\")
    print("      -m anthropic/claude-sonnet-4-5-20250929")
    print()
    print("  The -m flag sets self.model_name on the agent.")
    print("  LiteLLM supports many providers:")
    print()
    print("    anthropic/claude-sonnet-4-5-20250929   (Anthropic)")
    print("    openai/gpt-4o                          (OpenAI)")
    print("    openai/gemma4-e4b                      (LMStudio local)")
    print()
    print("  Required environment variables:")
    print("    ANTHROPIC_API_KEY   (for Anthropic models)")
    print("    OPENAI_API_KEY     (for OpenAI models)")
    print()


def run_evaluation() -> None:
    """Run the evaluation if an API key is available."""
    print("=" * 60)
    print("Step 6: Running the Evaluation")
    print("=" * 60)
    print()

    has_anthropic = bool(os.environ.get("ANTHROPIC_API_KEY"))
    has_openai = bool(os.environ.get("OPENAI_API_KEY"))

    if not has_anthropic and not has_openai:
        print("  No API key found (ANTHROPIC_API_KEY or OPENAI_API_KEY).")
        print("  To run this evaluation, set an API key and run:")
        print()
        print("    export ANTHROPIC_API_KEY=your-key-here")
        print("    harbor run -p tasks/llm-task \\")
        print("      --agent agent:LLMAgent \\")
        print("      -m anthropic/claude-sonnet-4-5-20250929")
        print()
        print("  Skipping evaluation run.")
        print()
        return

    model = "anthropic/claude-sonnet-4-5-20250929" if has_anthropic else "openai/gpt-4o"
    task_path = Path(__file__).parent / "tasks" / "llm-task"

    cmd = [
        "harbor", "run",
        "-p", str(task_path),
        "--agent", "agent:LLMAgent",
        "-m", model,
    ]

    print(f"  Running: {' '.join(cmd)}")
    print()
    print("-" * 60)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent),
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    print("-" * 60)

    if result.returncode == 0:
        print("\n  Evaluation completed successfully!")
    else:
        print(f"\n  Evaluation finished with return code {result.returncode}")
    print()


def show_summary() -> None:
    """Display lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("  Key takeaways:")
    print("  - LLM-powered agents use language models for reasoning")
    print("  - The agent-LLM-environment loop: ask -> execute -> check -> retry")
    print("  - self.model_name receives the -m flag from the harbor CLI")
    print("  - LiteLLM provides unified access to any model provider")
    print("  - Iterative refinement with error feedback improves success rates")
    print()
    print("  You have completed Module 4: Building Custom Agents!")
    print()
    print("  Next: Module 5 - Evaluating Real-World Agents")
    print("  Learn to evaluate Claude Code, Langchain, Langgraph, and more.")


def main() -> None:
    """Run the agent-with-llm lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Module 4, Lesson 4         #")
    print("#     LLM-Powered Custom Agent                         #")
    print("########################################################")
    print()

    show_concept()
    show_loop_diagram()
    show_agent_code()
    show_task()
    explain_running()
    run_evaluation()
    show_summary()


if __name__ == "__main__":
    main()
