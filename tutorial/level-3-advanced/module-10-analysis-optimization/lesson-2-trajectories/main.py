"""
Harbor Tutorial — Level 3, Module 10, Lesson 2: Agent Trajectories

Learn how to inspect and understand the complete execution trace of every
action an agent takes during a trial — every command, observation, and result.
"""

import json
import sys

from helpers import (
    TRIALS_DIR,
    check_prerequisites,
    get_atif_example,
    inspect_trial_output,
    run_trial,
)


def explain_trajectories() -> None:
    """Explain what agent trajectories are and why they matter."""
    print("=" * 60)
    print("STEP 1: What Are Agent Trajectories?")
    print("=" * 60)
    print()
    print("An agent trajectory is the complete execution trace of every")
    print("action an agent takes during a trial. It captures:")
    print()
    print("  - Every LLM call (prompt, response, model, tokens, cost)")
    print("  - Every tool invocation (commands run in the environment)")
    print("  - Every observation (command output, errors, file contents)")
    print("  - Timing data for each step")
    print()
    print("Trajectories are essential for:")
    print("  1. Debugging — understand WHY an agent failed or succeeded")
    print("  2. Optimization — find bottlenecks and wasted steps")
    print("  3. Comparison — see how different agents solve the same task")
    print("  4. Reproducibility — replay exactly what happened")
    print()
    print("Harbor records trajectories in ATIF (Agent Trajectory Interchange")
    print("Format) v1.7, a standardized JSON schema that works across all")
    print("agents and environments.")
    print()


def explain_atif_format() -> None:
    """Explain the ATIF trajectory format with a formatted example."""
    print("=" * 60)
    print("STEP 4: Understanding ATIF (Agent Trajectory Interchange Format)")
    print("=" * 60)
    print()
    print("ATIF v1.7 is Harbor's standardized schema for recording agent")
    print("trajectories. It provides a common format across all agents and")
    print("environments, making trajectories comparable and analyzable.")
    print()
    print("Schema structure:")
    print()
    print("  Trajectory (top level)")
    print("  |-- schema_version   : 'ATIF-v1.7'")
    print("  |-- agent            : {name, version, model_name}")
    print("  |-- steps[]          : ordered list of execution steps")
    print("  |    |-- step_id     : sequential integer (starts at 1)")
    print("  |    |-- timestamp   : ISO 8601 timestamp")
    print("  |    |-- source      : 'system', 'user', or 'agent'")
    print("  |    |-- message     : text content of the step")
    print("  |    |-- tool_calls[]: tools/commands the agent invoked")
    print("  |    |    |-- tool_call_id   : unique ID for this call")
    print("  |    |    |-- function_name  : tool name (e.g., 'bash')")
    print("  |    |    |-- arguments      : dict of arguments")
    print("  |    |-- observation : {results: [{source_call_id, content}]}")
    print("  |    |-- metrics     : {prompt_tokens, completion_tokens, cost_usd}")
    print("  |-- final_metrics    : aggregated totals across all steps")
    print("  |-- subagent_trajectories[] : embedded sub-agent traces")
    print()
    print("Agent steps include model info, token counts, and cost so you")
    print("can analyze both behavior and economics of each trial.")
    print()
    print("Example ATIF trajectory (abbreviated):")
    print()
    print(json.dumps(get_atif_example(), indent=2))
    print()


def explain_viewing_and_exporting() -> None:
    """Explain how to view and export trajectories."""
    print("=" * 60)
    print("STEP 5: Viewing and Exporting Trajectories")
    print("=" * 60)
    print()
    print("--- Viewing trajectories in the web UI ---")
    print()
    print("Harbor includes a built-in web viewer that renders trajectories")
    print("as an interactive timeline. Launch it with:")
    print()
    print(f"  harbor view {TRIALS_DIR}")
    print()
    print("The viewer auto-detects whether the folder contains jobs or")
    print("individual trials and displays them accordingly. You can expand")
    print("each step, view tool calls and observations, and see timing.")
    print()
    print("--- Exporting trajectories for external analysis ---")
    print()
    print("Use `harbor traces export` to extract trajectories into formats")
    print("suitable for analysis, fine-tuning, or sharing:")
    print()
    print(f"  harbor traces export -p {TRIALS_DIR}")
    print()
    print("Useful flags:")
    print("  --recursive / --no-recursive  Search subdirectories")
    print("  --episodes all|last           Export all episodes or just the last")
    print("  --sharegpt / --no-sharegpt    Export in ShareGPT format")
    print("  --filter success|failure|all  Filter by trial outcome")
    print("  --subagents / --no-subagents  Include sub-agent traces")
    print()
    print("Example — export only successful trials in ShareGPT format:")
    print()
    print(f"  harbor traces export -p {TRIALS_DIR} --filter success --sharegpt")
    print()


def print_recap() -> None:
    """Print a summary of what was covered."""
    print("=" * 60)
    print("RECAP")
    print("=" * 60)
    print()
    print("In this lesson you learned:")
    print()
    print("  1. Agent trajectories capture the complete execution trace of")
    print("     every action an agent takes during a trial.")
    print()
    print("  2. Trial output is organized into agent/, verifier/, artifacts/,")
    print("     config.json, result.json, and trial.log.")
    print()
    print("  3. ATIF v1.7 (Agent Trajectory Interchange Format) is Harbor's")
    print("     standardized schema: version, metadata, and ordered steps")
    print("     with tool_calls, observations, and metrics.")
    print()
    print("  4. `harbor view <folder>` launches a web UI to explore")
    print("     trajectories interactively.")
    print()
    print("  5. `harbor traces export` extracts trajectories for external")
    print("     analysis, fine-tuning, or sharing.")
    print()
    print("Next lesson: Sweeps — systematically vary parameters to find")
    print("optimal agent configurations.")
    print()


def main() -> None:
    """Run all lesson steps."""
    print()
    print("=" * 60)
    print("  HARBOR TUTORIAL")
    print("  Level 3 | Module 10 | Lesson 2: Agent Trajectories")
    print("=" * 60)
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_trajectories()

    print("=" * 60)
    print("STEP 2: Running a Trial to Generate a Trajectory")
    print("=" * 60)
    print()
    trial_dir = run_trial()

    if trial_dir:
        print("=" * 60)
        print("STEP 3: Inspecting Trial Output Structure")
        print("=" * 60)
        print()
        print("A trial directory contains everything about one agent attempt:")
        print()
        inspect_trial_output(trial_dir)

    explain_atif_format()
    explain_viewing_and_exporting()
    print_recap()


if __name__ == "__main__":
    main()
