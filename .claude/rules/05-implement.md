---
description: "Step 3: Implement — coding rules and this project's layout"
---

# Step 3: Implement

Write clean code from the start. Follow these rules during implementation:

- Do NOT commit via `git` unless explicitly instructed by the user
- When creating diagrams or graphs, use `mermaid`
- Write clean code from the start — don't plan to "clean it up later"
- Refactor continuously — improve code structure immediately when you see issues
- Remove dead code — delete unused functions, variables, imports, and commented code
- Before changing any signature, renaming, or deleting something shared, find
  every caller with `findReferences` where the `LSP` tool is available — grep
  misses the ones spelled differently and finds ones that are not calls.
  [`lsp.md`](lsp.md)
- After writing code: review comments, clean up imports, check for side effects

<!-- Below: one section per top-level area of the repo, naming what belongs
     there and what must NOT. Derived from the real directory tree — do not
     invent structure the repo does not have. -->

## `tutorial/` — the lessons

Belongs here: lesson leaves, each self-contained, following the naming and file
layout in [`tutorial-structure.md`](tutorial-structure.md) and the README format
in [`lesson-content.md`](lesson-content.md).

Must NOT be here:

- **Shared code between lessons.** A lesson is self-contained by definition — a
  learner clones, `cd`s in, and runs it. If two lessons need the same helper,
  duplicate it; that is the intended cost.
- **A workspace of any kind.** No uv workspace, no shared `.venv`, no root
  `pyproject.toml`. Each leaf resolves independently.
- **Committed `jobs/` or `trials/` output.** Both are gitignored; they are Harbor
  run artifacts, not source.
- **`main.py` over ~200 lines.** Split helpers into a sibling module in the same
  lesson directory.

## `infra/` — the shared support stack

Belongs here: `docker-compose.yaml`, `litellm/config.yaml`, `verify.py`,
`.env.example`, and the README explaining the quick start.

Must NOT be here: anything a single lesson needs — that goes in the lesson. And
never a real credential: `.env` is gitignored and stays that way, hosted-provider
keys are blank in `.env.example` by design. See
[`12-security.md`](12-security.md).

## `syllabus.md` — the source of truth

Belongs here: the lesson list, topics and ordering. **Changing the structure of
this file requires confirmation** — lessons reference each other by number, so
reordering it silently invalidates cross-references throughout `tutorial/`.

## `.claude/` — agent configuration

Belongs here: this workflow. The numbered files are the generic contract; the
five unnumbered ones (`tutorial-structure`, `lesson-content`, `harbor-patterns`,
`coding-standards`, `references`) are this project's own knowledge and win where
they overlap.

## Repository structure

```text
harbor-tutorial/
├── syllabus.md                      source of truth: lesson list + ordering
├── README.md
├── pyrightconfig.json               one executionEnvironments entry per leaf
├── .hadolint.yaml                   Dockerfile lint opt-in
├── .mcp.json                        playwright-harbor-tutor
├── .claude/
│   ├── CLAUDE.md
│   ├── settings.json
│   ├── hooks/                       playwright desktop hooks
│   └── rules/                       01–12 + 5 project-specific files
├── infra/
│   ├── docker-compose.yaml          qdrant + litellm
│   ├── litellm/config.yaml          model aliases + fallback chain
│   ├── verify.py                    prerequisite checker
│   ├── .env.example                 committed template (.env is gitignored)
│   └── pyproject.toml
└── tutorial/
    ├── level-1-foundations/         module-01 … module-03   (11 lessons)
    ├── level-2-intermediate/        module-04 … module-08   (22 lessons)
    └── level-3-advanced/            module-09 … module-12   (14 lessons)
```
