---
globs: ["tutorial/**"]
---

# Tutorial Structure Rules

Always consult `syllabus.md` for the concrete module/lesson breakdown. This file defines conventions, not content.

## Lesson Directory Convention

Every lesson lives in `tutorial/<level>/<module>/<lesson>/` and must contain:

1. **`pyproject.toml`** — standalone `uv` project with `name`, `version`, `description`, `requires-python`, and `dependencies`.
2. **`main.py`** — working lesson code. Primary deliverable.
3. **`README.md`** — lesson guide (see `lesson-content.md` for format).
4. **`.gitignore`** — ignore `.venv/`, `__pycache__/`, `*.pyc`, `.python-version`, `jobs/`, `trials/`.

Some lessons may also include:
- **Task directories** — Harbor task format (`instruction.md`, `task.toml`, `environment/`, `tests/`, `solution/`)
- **`job.yaml`** — Harbor job configuration

## pyproject.toml Template

```toml
[project]
name = "harbor-tutorial-L<level>-M<module>-<lesson>"
version = "0.1.0"
description = "<Lesson title from syllabus>"
requires-python = ">=3.12"

[project.dependencies]
harbor = ">=0.16"
# Add lesson-specific deps here

[tool.ruff]
# Lint/format policy lives in the repo-root ruff.toml. Pull it in explicitly:
# a leaf carrying [tool.ruff] SHADOWS the root config rather than merging with
# it, so without this line the lesson silently runs ruff's own defaults
# (413 rules, line-length 88) while looking correctly configured.
extend = "../../../../ruff.toml"
# This lesson directory is its own source root, so sibling modules
# (results.py, helpers.py, agent.py) sort as first-party imports
# whether ruff is invoked here or from the repo root.
src = ["."]
```

> The `extend` path above assumes the standard depth
> `tutorial/<level>/<module>/<lesson>/`. Count the directories if you nest
> differently — a wrong relative path makes ruff fail to find the file rather
> than fall back silently, so `ruff check .` in the new leaf will tell you.

## .gitignore Template

```text
.venv/
__pycache__/
*.pyc
.python-version
jobs/
trials/
```

## Principles

- Each lesson must be fully self-contained — `cd` into it, run `uv sync && uv run python main.py`, see results.
- Lessons that run evaluations assume Docker is installed and running.
- Print meaningful output to the console so the user can follow along.
- Keep `main.py` under ~200 lines. Extract helpers into a separate module in the same directory if needed.
- Include task directories for lessons that create or work with Harbor tasks.
- Include `job.yaml` for lessons that configure multi-trial evaluation runs.
