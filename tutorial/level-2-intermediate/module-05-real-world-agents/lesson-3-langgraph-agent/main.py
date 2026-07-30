"""
Lesson 3: Langgraph Agent in Harbor

Wrap a LangGraph 1.x StateGraph agent as a Harbor BaseAgent. The graph-based
approach gives explicit control over the agent's reasoning flow through nodes
and edges. The model is served by the LiteLLM proxy (Gemma 4).
"""

import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

LESSON_DIR = Path(__file__).parent

#: Alias defined in agent-eval-benchmark/infra/litellm/config.yaml (Gemma 4 26B).
MODEL = "gemma-large"


def litellm_root() -> str:
    """The LiteLLM gateway root URL (base URL without the /v1 suffix)."""
    base = os.environ.get("LITELLM_BASE_URL", "http://localhost:4000/v1")
    return base.removesuffix("/v1")


def check_prerequisites() -> bool:
    """Verify Docker, Harbor CLI, and the LiteLLM gateway."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
    print("=" * 60)

    ok = True

    if shutil.which("docker"):
        result = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, check=False
        )
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

    try:
        urllib.request.urlopen(f"{litellm_root()}/health/liveliness", timeout=5)
        print(f"  [OK] LiteLLM gateway is reachable at {litellm_root()}")
    except (urllib.error.URLError, OSError):
        print(f"  [FAIL] LiteLLM gateway is not reachable at {litellm_root()}")
        print("         Start the stack from agent-eval-benchmark:")
        print("             cd agent-eval-benchmark/infra && podman compose up -d")
        print("         (for local models: lms server start && lms load google/gemma-4-e4b)")
        ok = False

    print()
    return ok


def explain_langgraph() -> None:
    """Explain LangGraph's StateGraph approach."""
    print("=" * 60)
    print("Step 2: LangGraph vs create_agent()")
    print("=" * 60)
    print()
    print("In Lesson 2, create_agent() built the ReAct loop for us. LangGraph")
    print("is what it builds on — here we assemble that graph ourselves.")
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
    print("  Benefits of building the graph explicitly:")
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
    print("  graph.add_edge(START, 'chatbot')")
    print("  graph.add_conditional_edges('chatbot', tools_condition,")
    print("      {'tools': 'tools', END: END})")
    print("  graph.add_edge('tools', 'chatbot')")
    print("  compiled = graph.compile()")
    print("  await compiled.ainvoke(state, {'recursion_limit': 50})")
    print()


def run_evaluation() -> None:
    """Run the evaluation with the LangGraph agent."""
    print("=" * 60)
    print("Step 4: Running Evaluation")
    print("=" * 60)
    print()

    task_path = LESSON_DIR / "tasks" / "multi-step-task"
    agent_path = "agent:LanggraphHarborAgent"

    cmd = [
        "harbor", "run",
        "-p", str(task_path),
        "--agent", agent_path,
        "-m", MODEL,
    ]

    print(f"Running: {' '.join(cmd)}")
    print()
    print("-" * 60)

    # PYTHONPATH makes `agent:LanggraphHarborAgent` importable in the
    # harbor subprocess — cwd alone is not on its sys.path.
    env = {**os.environ, "PYTHONPATH": str(LESSON_DIR)}
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(LESSON_DIR),
        env=env,
        check=False,
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
    """Inspect evaluation results from the most recent job."""
    print("=" * 60)
    print("Step 5: Results")
    print("=" * 60)
    print()

    jobs_dir = LESSON_DIR / "jobs"
    job_dirs = sorted(d for d in jobs_dir.glob("*") if d.is_dir()) if jobs_dir.exists() else []
    if not job_dirs:
        print("  No jobs/ directory found.")
        return

    # Each job dir holds one result.json summarising the job, plus one per
    # trial in a subdirectory. The trial files carry the rewards.
    for result_file in sorted(job_dirs[-1].glob("*/result.json")):
        try:
            data = json.loads(result_file.read_text())
            rewards = (data.get("verifier_result") or {}).get("rewards") or {}

            print(f"  Task: {data.get('task_name', 'unknown')}")
            print(f"  Reward: {rewards.get('reward', 0.0)}")

            started, finished = data.get("started_at"), data.get("finished_at")
            if started and finished:
                duration = (
                    datetime.fromisoformat(finished) - datetime.fromisoformat(started)
                ).total_seconds()
                print(f"  Duration: {duration:.1f}s")

            if data.get("exception_info"):
                print(f"  Exception: {data['exception_info']}")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"  Error reading {result_file.name}: {e}")

    print()


def show_summary() -> None:
    """Display lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("In this lesson you learned:")
    print("  - How LangGraph's StateGraph differs from create_agent()")
    print("  - How to build nodes (chatbot, tools) and conditional edges")
    print("  - How tools_condition routes between tool calls and END")
    print("  - How to wrap a LangGraph agent as a Harbor BaseAgent")
    print("  - Models route through the LiteLLM proxy (gemma-large = Gemma 4)")
    print("  - Multi-step tasks that test sequential reasoning")
    print()
    print("Next lesson: lesson-4-deepagents-agent (Deepagents framework in Harbor)")


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
