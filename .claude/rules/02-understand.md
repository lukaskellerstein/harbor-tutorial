---
description: "Step 1: Understand — read code, ask questions, identify gaps before any implementation"
---

# Step 1: Understand

- Read relevant code and identify impacted areas
- Baseline the repo's existing problems: `nvim-tools --json --all` (every
  linter / formatter / type-checker finding, repo-wide) — so pre-existing
  findings are distinguishable from ones you introduce. For performance or
  RAM questions, `lukas-ps --json [name]` measures the actual process tree.
  Both are described in `CLAUDE.md` § Read-only inspection.
- Ask clarifying questions if requirements are ambiguous
- Identify gaps in the current design and opportunities for improvement
- Understand the requirement completely before proceeding
- **For bug reports**: reproduce the issue first (`cd <lesson> && uv sync &&
  uv run python main.py`, with Docker running) to confirm the problem before
  attempting a fix

## Before touching a lesson

Two reads are not optional here, because guessing at either is the failure mode
this project actually hits:

1. **`syllabus.md`** — it is the source of truth for which lessons exist, what
   each one teaches and in what order. A lesson that contradicts the syllabus is
   a bug in the lesson.
2. **The Harbor source at `~/Projects/Github/harbor-framework/harbor`** — read
   the real CLI flags, API signatures and config formats. Do not infer them from
   another lesson, from the docs site, or from memory; `harbor-patterns.md`
   records where each area lives.

Lessons reference each other by number and build on one another, so read the
neighbouring lessons before changing one in the middle.
