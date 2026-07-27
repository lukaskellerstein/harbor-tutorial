"""
Test approach definitions for the test-scripts lesson.

Each approach describes a different strategy for writing Harbor test scripts.
"""

APPROACHES: list[dict[str, str]] = [
    {
        "number": "1",
        "title": "Binary Test (Pass/Fail)",
        "task": "binary-test",
        "expected_reward": "1",
        "description": (
            "The simplest approach. The test checks a single condition\n"
            "  and writes either 0 (fail) or 1 (pass). There is no\n"
            "  partial credit.\n\n"
            "  When to use:\n"
            "  - Simple tasks with a clear right/wrong answer\n"
            "  - File existence checks\n"
            "  - Exact output matching"
        ),
    },
    {
        "number": "2",
        "title": "Partial-Credit Test",
        "task": "partial-credit",
        "expected_reward": "1.00 (0.33 per function)",
        "description": (
            "This test checks multiple criteria independently and\n"
            "  calculates a fractional reward. Each correct function\n"
            "  earns 1/3 of the total.\n\n"
            "  When to use:\n"
            "  - Tasks with multiple independent requirements\n"
            "  - Benchmarks where partial progress matters\n"
            "  - Comparing agent capability across subtasks"
        ),
    },
    {
        "number": "3",
        "title": "Pytest-Based Test with CTRF",
        "task": "pytest-test",
        "expected_reward": "1",
        "description": (
            "This approach uses pytest for structured testing and\n"
            "  produces a CTRF (Common Test Report Format) JSON file.\n"
            "  This is Harbor's DEFAULT scaffolding style.\n\n"
            "  test.sh installs uv, then uses uvx to run pytest with\n"
            "  the pytest-json-ctrf plugin. A separate test_state.py\n"
            "  file contains the actual test cases.\n\n"
            "  When to use:\n"
            "  - Complex tasks with many test cases\n"
            "  - When you want structured test reporting\n"
            "  - When tests need Python assertions and fixtures"
        ),
    },
]
