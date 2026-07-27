"""
Lesson 2: Core Concepts

This lesson explains the six core building blocks of Harbor:
Task, Dataset, Agent, Environment, Trial, and Job.
No evaluation is run — this is a conceptual lesson with
inline examples and directory structure exploration.
"""

from concepts import (
    explain_agent,
    explain_dataset,
    explain_environment,
    explain_job,
    explain_task,
    explain_trial,
    explore_example_task,
    show_relationships,
)


def show_summary() -> None:
    """Display a summary of all concepts."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("Harbor's six core concepts:")
    print()
    print("  1. TASK        - What to do (instruction + env + test)")
    print("  2. DATASET     - Collection of tasks")
    print("  3. AGENT       - Program that solves tasks")
    print("  4. ENVIRONMENT - Isolated container workspace")
    print("  5. TRIAL       - One agent attempt at one task")
    print("  6. JOB         - Collection of trials")
    print()
    print("The evaluation flow:")
    print("  Task + Agent + Environment --> Trial --> Reward (0-1)")
    print("  Multiple Trials            --> Job   --> Aggregate Metrics")
    print()
    print("Next lesson: lesson-3-viewing-results (inspecting trial outputs)")


def main() -> None:
    """Run the core-concepts lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Lesson 2                   #")
    print("#          Core Concepts                                #")
    print("########################################################")
    print()

    explain_task()
    explain_dataset()
    explain_agent()
    explain_environment()
    explain_trial()
    explain_job()
    show_relationships()
    explore_example_task()
    show_summary()


if __name__ == "__main__":
    main()
