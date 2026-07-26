"""A data processing module with error handling issues."""

import json
from typing import Any


def load_json(filepath: str) -> dict[str, Any]:
    # Bug: no error handling for missing file or invalid JSON
    with open(filepath) as f:
        return json.load(f)


def transform_records(records: list[dict]) -> list[dict]:
    """Add an 'id' field to each record."""
    result = []
    for i, record in enumerate(records):
        record["id"] = i  # Bug: mutates the original dict
        result.append(record)
    return result


def filter_by_field(
    records: list[dict], field: str, value: Any
) -> list[dict]:
    # Bug: no handling for missing field in record
    return [r for r in records if r[field] == value]


def summarize(records: list[dict]) -> dict[str, int]:
    return {
        "total": len(records),
        "fields": len(records[0].keys()) if records else 0,
    }


if __name__ == "__main__":
    data = [{"name": "Alice"}, {"name": "Bob"}]
    transformed = transform_records(data)
    print(f"Transformed: {transformed}")
    print(f"Original mutated: {data}")  # Demonstrates the mutation bug
