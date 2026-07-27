"""
Task component definitions for the task-anatomy lesson.

Describes each file in a Harbor task directory and its role.
"""

COMPONENTS: list[dict[str, str]] = [
    {
        "file": "instruction.md",
        "title": "Instruction",
        "description": (
            "A natural-language description of what the agent must do.\n"
            "  This is the ONLY information the agent receives. It should be\n"
            "  clear, self-contained, and specify exactly what output is expected."
        ),
    },
    {
        "file": "task.toml",
        "title": "Task Configuration",
        "description": (
            "Metadata and configuration for the task. Includes the task name\n"
            "  (org/name format), author info, difficulty, timeouts for the\n"
            "  agent and verifier, and environment build settings."
        ),
    },
    {
        "file": "environment/Dockerfile",
        "title": "Environment Dockerfile",
        "description": (
            "Defines the Docker container where the agent works. This is the\n"
            "  sandbox -- the agent can only see and modify files inside this\n"
            "  container. Pre-install any tools or data the task requires."
        ),
    },
    {
        "file": "tests/test.sh",
        "title": "Test Script (Verifier)",
        "description": (
            "Runs AFTER the agent finishes. Checks the agent's work and writes\n"
            "  a reward (float 0-1) to /logs/verifier/reward.txt. This is how\n"
            "  Harbor measures success. 1 = perfect, 0 = failure."
        ),
    },
    {
        "file": "solution/solve.sh",
        "title": "Reference Solution",
        "description": (
            "A known-good solution for the task. The oracle agent runs this\n"
            "  script to validate that the task and tests work correctly.\n"
            "  Optional but highly recommended for task development."
        ),
    },
]
