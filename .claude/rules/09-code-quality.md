---
description: "Reference: Code quality standards — SOLID, KISS, DRY, error handling, anti-patterns"
---

# Reference: Code Quality

Write code that is **simple, maintainable, and production-ready**. Prioritize
clarity over cleverness.

> This is the generic standard. Where it disagrees with
> [`coding-standards.md`](coding-standards.md) — this project's own Python rules
> for tutorial code — that file wins. Tutorial code is optimised to be *read*,
> which occasionally means a more explicit, longer form than production code
> would use.

## Principles

1. **Simplicity First** (KISS)
2. **Consistency** in tech stack
3. **Maintainability** over cleverness
4. **DRY** — eliminate duplication
5. **YAGNI** — don't add speculative features
6. **SOLID** — Single Responsibility, Open/Closed, Liskov Substitution,
   Interface Segregation, Dependency Inversion

**The DRY exception in this repo**: lessons are self-contained on purpose, so
duplication *across* leaves is correct and must not be refactored into a shared
module. DRY applies within a lesson, not between them.

## Code Organization

- Keep functions small (< 20 lines ideally, < 100 lines max)
- One level of abstraction per function
- Use meaningful, pronounceable names
- Self-documenting code; comments explain "why", not "what"
- Prefer composition over inheritance

## Error Handling

- Fail fast and explicitly
- Use typed errors/exceptions with clear messages
- Never silently ignore errors
- Validate inputs at system boundaries

## Anti-Patterns to Avoid

- No commented-out code "just in case"
- No TODO comments
- No copy-paste instead of abstracting
- No premature optimization
- No over-engineering simple solutions
- No ignoring compiler/linter warnings

## Formatting and linting

This machine runs "no config, no tool": a formatter or linter acts on this repo
only if the repo carries that tool's own config file. If `:w` changes nothing and
the gutter stays empty, the marker file is missing — not the editor broken.

This repo opts in to:

| Tool | Marker | Covers |
|:--|:--|:--|
| ruff (format + lint + live server) | root `ruff.toml`, pulled into each leaf by `extend` | the 240 Python files |
| basedpyright | `pyrightconfig.json` (one entry per leaf) | type checking, repo-wide |
| hadolint | `.hadolint.yaml` | every task `environment/Dockerfile` |
| shfmt | `.editorconfig` | the `solve.sh` / `test.sh` scripts |
| shellcheck | `.shellcheckrc` | same |
| markdownlint-cli2 | `.markdownlint-cli2.yaml` | every lesson README |

> **The `extend` line in each leaf's `[tool.ruff]` is load-bearing.** A leaf
> carrying `[tool.ruff]` *shadows* the root `ruff.toml` outright rather than
> merging with it — delete the `extend` and that leaf silently drops to ruff's
> own defaults (413 rules, line-length 88) while still looking configured. Keep
> the line when adding a lesson; the relative depth is `../../../../ruff.toml`
> from a lesson leaf, `../ruff.toml` from `infra/`.

Nothing here formats YAML or TOML — that is expected, not a gap.

The contract, and the skill that applies it, are in mac-setup:
`projects/tooling.md` and `/lint-format-lsp`.
