"""
Lesson 3: Langgraph Agent in Harbor

Wrap a LangGraph stateful graph agent as a Harbor BaseAgent.
The graph-based approach gives explicit control over agent
reasoning flow through nodes and edges.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


LESSON_DIR = Path(__file__).parent


def check_prerequisites() -> bool:
    """Verify Docker, Harbor CLI, and API keys."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
    print("=" * 60)

    ok = True

    if shutil.which("docker"):
        result = subprocess.run(["docker", "info"], capture_output=True, text=True)
        if result.returncode == 0:
            print("  [OK] Docker is running")
        else:
            print("  [FAIL] Docker daemon is not running")
            ok = False
    else:
        print("  [FAIL] Docker CLI not found")
        ok = False

    if shutil.which("harbor"):
        print("  [OK] Harbor CLI is installed")
    else:
        print("  [FAIL] Harbor CLI not found")
        ok = False

    if os.environ.get("OPENAI_API_KEY"):
        print("  [OK] OPENAI_API_KEY is set")
    else:
        print("  [WARN] OPENAI_API_KEY is not set")
        ok = False

    print()
    return ok


def explain_langgraph() -> None:
    """Explain LangGraph's StateGraph approach."""
    print("=" * 60)
    print("Step 2: LangGraph vs Langchain Agent Patterns")
    print("=" * 60)
    print()
    print("In Lesson 2, we used a simple while-loop agent pattern.")
    print("LangGraph takes a different approach: explicit state graphs.")
    print()
    print("  StateGraph components:")
    print("    - State:  TypedDict defining the data flowing through the graph")
    print("    - Nodes:  Functions that transform state (chatbot, tools)")
    print("    - Edges:  Connections between nodes (including conditional)")
    print()
    print("  Graph structure for our agent:")
    print()
    print("    [START] -> [chatbot] --(has tool calls)--> [tools]")
    print("                  ^                               |")
    print("                  |_______________________________|")
    print("                  |")
    print("           (no tool calls)")
    print("                  |")
    print("                [END]")
    print()
    print("  Benefits of the graph approach:")
    print("    - Explicit, visible control flow")
    print("    - Easy to add new nodes (planning, reflection, etc.)")
    print("    - Built-in recursion limits and checkpointing")
    print("    - Composable with other graphs")
    print()


def show_graph_code() -> None:
    """Show the key graph construction code."""
    print("=" * 60)
    print("Step 3: Graph Construction")
    print("=" * 60)
    print()
    print("  See agent.py for full code. Key construction pattern:")
    print()
    print("  graph = StateGraph(AgentState)")
    print("  graph.add_node('chatbot', chatbot)")
    print("  graph.add_node('tools', ToolNode(tools))")
    print("  graph.set_entry_point('chatbot')")
    print("  graph.add_conditional_edges('chatbot', should_continue,")
    print("      {'tools': 'tools', END: END})")
    print("  graph.add_edge('tools', 'chatbot')")
    print("  compiled = graph.compile()")
    print()


def run_evaluation() -> None:
    """Run the evaluation with the LangGraph agent."""
    print("=" * 60)
    print("Step 4: Running Evaluation")
    print("=" * 60)
    print()

    task_path = LESSON_DIR / "tasks" / "multi-step-task"
    agent_path = "agent:LanggraphHarborAgent"
    model = "openai/gpt-4o"

    cmd = [
        "harbor", "run",
        "-p", str(task_path),
        "--agent", agent_path,
        "-m", model,
    ]

    print(f"Running: {' '.join(cmd)}")
    print()
    print("-" * 60)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(LESSON_DIR),
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    print("-" * 60)

    if result.returncode == 0:
        print("\nEvaluation completed!")
    else:
        print(f"\nEvaluation exited with code {result.returncode}")
    print()


def inspect_results() -> None:
    """Inspect evaluation results."""
    print("=" * 60)
    print("Step 5: Results")
    print("=" * 60)
    print()

    jobs_dir = LESSON_DIR / "jobs"
    if not jobs_dir.exists():
        print("  No jobs/ directory found.")
        return

    for result_file in sorted(jobs_dir.rglob("result.json")):
        try:
            data = json.loads(result_file.read_text())
            task_name = data.get("task", {}).get("name", "unknown")
            reward = data.get("reward", 0.0)
            print(f"  Task: {task_name}")
            print(f"  Reward: {reward}")
            duration = data.get("duration_sec")
            if duration is not None:
                print(f"  Duration: {duration:.1f}s")
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  Error reading results: {e}")

    print()


def show_summary() -> None:
    """Display lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("In this lesson you learned:")
    print("  - How LangGraph's StateGraph differs from simple agent loops")
    print("  - How to build nodes (chatbot, tools) and conditional edges")
    print("  - How to wrap a LangGraph agent as a Harbor BaseAgent")
    print("  - Multi-step tasks that test sequential reasoning")
    print()
    print("Next lesson: deepagents-agent (Deepagents framework in Harbor)")


def main() -> None:
    """Run the langgraph-agent lesson."""
    print()
    print("########################################################")
    print("#  HARBOR TUTORIAL - Level 2, Module 5, Lesson 3       #")
    print("#  Langgraph Agent in Harbor                           #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_langgraph()
    show_graph_code()
    run_evaluation()
    inspect_results()
    show_summary()


if __name__ == "__main__":
    main()
