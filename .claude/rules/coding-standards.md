---
globs: ["tutorial/**/*.py"]
---

# Python Coding Standards for Tutorial Code

## Style

- Target Python 3.12+. Use type hints on function signatures.
- Use `if __name__ == "__main__":` guard in every `main.py`.
- Use `asyncio.run(main())` for async lessons (e.g., custom agents).
- Import order: stdlib, third-party, local — separated by blank lines.
- Use f-strings for string formatting.
- Keep functions short and focused — this is tutorial code, readability is paramount.

## Harbor Interaction

- Harbor is CLI-first. Most lessons invoke `harbor` via subprocess or instruct the user to run CLI commands.
- Python API is used only for custom agents (`BaseAgent`, `BaseInstalledAgent`) and adapters.
- Always verify CLI flags and API signatures against the Harbor source code before using them.

## Async Patterns

Agent and environment operations are async:

```python
import asyncio

async def main():
    await environment.exec(command="echo 'hello'")
    await agent.setup(environment)
    await agent.run(instruction, environment, context)

asyncio.run(main())
```

## Error Handling

- Check Docker is running before attempting evaluations.
- Print clear error messages if prerequisites are not met.
- Do not silently swallow exceptions — this is educational code.

## Dependencies

- Use `uv add` to add dependencies, never `pip install`.
- Primary dependency for all lessons: `harbor`.

## Console Output

Print section headers and results so users can follow along:

```python
print("=" * 60)
print("Step 1: Scaffolding a new Harbor task")
print("=" * 60)
```

Print key results inline — trial rewards, task status, agent output.
