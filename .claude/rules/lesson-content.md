---
globs: ["tutorial/**/README.md"]
---

# Lesson Content — README.md Format

Every lesson's README.md must follow this template:

```markdown
# <Lesson Title>

**Duration:** <estimated time>

## Overview
<2-3 sentences: what the user will learn and why it matters>

## Prerequisites
- <list prior lessons>
- <tools/services that must be running>

## Concepts
<Explain key concepts before code. Teach the "why".>

## Step-by-Step

### Step 1: <Action>
<Explain what and why, then show code>

### Step 2: <Action>
...

## Running the Lesson

```bash
cd tutorial/<level>/<module>/<lesson>
uv sync
uv run python main.py
```

## Expected Output

<Show what the user should see in the terminal>

## Key Takeaways

- <3-5 bullet points>

## Next Steps

<Point to the next lesson>
```

## Writing Rules

- Write for developers who know Python but may be new to Harbor and agent evaluation.
- Explain concepts before showing code — don't just dump code.
- One concept at a time. Progressive disclosure.
- Always explain WHY, not just WHAT.
- Every concept must have a working code example.
- Include "Expected Output" so users can verify results.
- For CLI-heavy lessons, show exact commands and expected output.
- For task-creation lessons, show the full task directory structure.
