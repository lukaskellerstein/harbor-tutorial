"""The 23 built-in RewardKit criteria, grouped by what they inspect.

Source: packages/rewardkit/src/rewardkit/criteria/ in the Harbor repo.
Every one of them also accepts `weight=`, `name=` and `isolated=`.
"""

CATALOGUE: dict[str, list[tuple[str, str]]] = {
    "Files": [
        ("file_exists(path)", "file is present"),
        ("file_not_exists(path)", "file is absent"),
        ("file_contains(path, text)", "substring present"),
        ("file_contains_regex(path, pattern)", "regex matches"),
        ("file_matches(path, expected)", "whole file equals (stripped)"),
        ("files_equal(path1, path2)", "two files identical"),
        ("diff_ratio(path, expected)", "FLOAT: similarity 0.0-1.0"),
    ],
    "Commands": [
        ("command_succeeds(cmd, cwd=, timeout=)", "exit code 0"),
        ("command_output_contains(cmd, text)", "stdout contains"),
        ("command_output_matches(cmd, expected)", "stdout equals (stripped)"),
        ("command_output_matches_regex(cmd, pattern)", "stdout matches regex"),
    ],
    "Structured data": [
        ("json_key_equals(path, key, expected)", "top-level JSON key"),
        ("json_path_equals(path, json_path, expected)", "dotted path, ints index lists"),
        ("csv_cell_equals(path, row, col, expected)", "CSV cell"),
        ("xlsx_cell_equals(path, cell, expected)", "needs the [documents] extra"),
        ("sqlite_query_equals(db, query, expected)", "first column of first row"),
    ],
    "Network": [
        ("http_status_equals(url, status=200)", "HTTP status code"),
        ("http_response_contains(url, text)", "response body contains"),
    ],
    "Images": [
        ("image_similarity(path1, path2)", "FLOAT: pixel match ratio"),
        ("image_size_equals(path, w, h)", "dimensions; needs Pillow"),
    ],
    "Trajectory (lesson 6)": [
        ("trajectory_tool_used(tool, min_count=1)", "agent called a tool"),
        ("trajectory_tool_not_used(tool)", "agent avoided a tool"),
        ("trajectory_turn_count(max_turns)", "FLOAT: partial credit for brevity"),
    ],
}


def print_catalogue() -> None:
    """Print the catalogue as a grouped table."""
    for group, entries in CATALOGUE.items():
        print(f"  {group}")
        for signature, description in entries:
            print(f"    {signature:<46} {description}")
        print()
