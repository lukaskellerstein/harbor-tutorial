# Prompt Templates

**Duration:** 30-45 minutes

## Overview

Learn how to use prompt templates to structure and enhance the instructions given to your Harbor agents. Prompt templates use Jinja2 syntax to wrap raw task instructions with system prompts, guidelines, and formatting -- giving you consistent agent behavior without modifying task files.

## Prerequisites

- Completed Lesson 2: Custom Installed Agent
- Docker installed and running
- Harbor CLI installed (`uv tool install harbor`)

## Concepts

### Prompt Templates (Jinja2)

A prompt template is a Jinja2 file (`.md.j2`) that wraps the raw task instruction with additional context. The template uses the `{{ instruction }}` placeholder, which gets replaced with the actual task instruction at runtime.

For example, a template might add system prompts, coding standards, or a specific persona before the task instruction:

```jinja2
You are a careful coding agent. Follow these rules:
1. Read the instruction carefully
2. Write clean, well-documented code

## Task
{{ instruction }}

## Guidelines
- Use Python 3.12+ syntax
- Add type hints to all functions
```

When the raw instruction is "Write a fibonacci function", the rendered prompt includes all the wrapper text plus the raw instruction injected at the `{{ instruction }}` placeholder.

### The @with_prompt_template Decorator

The `@with_prompt_template` decorator automates template rendering for `BaseInstalledAgent` subclasses. Apply it to your `run()` method:

```python
@with_prompt_template
async def run(self, instruction, environment, context):
    # 'instruction' is already rendered through the template!
    ...
```

Under the hood, the decorator:
1. Intercepts the `run()` call before your code executes
2. Calls `self.render_instruction(instruction)` which loads the Jinja2 template
3. Renders `{{ instruction }}` with the raw task instruction
4. Passes the fully rendered prompt as the `instruction` parameter to your method

The template file path is configured via the `prompt_template_path` kwarg, which can be set in `job.yaml` or via the `--agent-kwarg` CLI flag.

### SKILL.md Files

Skills are markdown files placed in `skills/<skill-name>/SKILL.md` that provide domain-specific knowledge to agents. Agents that support skills load these files during setup and inject their content into the agent's context.

Skills complement prompt templates -- templates control how instructions are formatted, while skills provide the domain knowledge an agent needs to solve tasks effectively.

## Step-by-Step

### Step 1: Create a Template File

Create `templates/template.md.j2` with a Jinja2 template that wraps the task instruction:

```jinja2
You are a careful coding agent. Follow these rules:
1. Read the instruction carefully
2. Write clean, well-documented code
3. Test your work before declaring done

## Task
{{ instruction }}

## Guidelines
- Use Python 3.12+ syntax
- Add type hints to all functions
- Include docstrings
- Handle edge cases gracefully
```

The `{{ instruction }}` placeholder is required -- Harbor's template renderer validates that it exists.

### Step 2: Understand the Decorator

Apply `@with_prompt_template` to your agent's `run()` method:

```python
from harbor.agents.installed.base import BaseInstalledAgent, with_prompt_template

class TemplatedAgent(BaseInstalledAgent):
    @with_prompt_template
    async def run(self, instruction, environment, context):
        # instruction is now the rendered template with the task embedded
        ...
```

### Step 3: Create a SKILL.md File

Create `skills/solve-task/SKILL.md` with domain knowledge:

```markdown
# Solve Task Skill

When solving a programming task:
1. **Understand** the requirements fully before writing code
2. **Plan** your approach
3. **Implement** with clean, readable code
4. **Test** your solution
5. **Verify** the output
```

### Step 4: Run with a Template

Pass the template path when running the evaluation:

```bash
harbor run -p tasks/code-task -a agent:TemplatedAgent \
    --agent-kwarg prompt_template_path=templates/template.md.j2
```

Or configure it in `job.yaml`:

```yaml
agents:
  - name: agent:TemplatedAgent
    kwargs:
      prompt_template_path: templates/template.md.j2
```

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-4-custom-agents/prompt-templates
uv sync
uv run python main.py
```

## Expected Output

```
########################################################
#          HARBOR TUTORIAL - Module 4, Lesson 3         #
#     Prompt Templates                                  #
########################################################

============================================================
Step 0: Checking Prerequisites
============================================================

  Docker installed and running: [OK]
  Harbor CLI installed:         [OK]

============================================================
Step 1: What Are Prompt Templates?
============================================================

  Prompt templates are Jinja2 templates that WRAP the raw task
  instruction before it reaches your agent's run() method.
  ...

============================================================
Step 3: Template Rendering Demo
============================================================

  RAW INSTRUCTION:
    Write a Python function that adds two numbers.

  RENDERED (after template):
    You are a careful coding agent. Follow these rules:
    1. Read the instruction carefully
    2. Write clean, well-documented code
    3. Test your work before declaring done

    ## Task
    Write a Python function that adds two numbers.

    ## Guidelines
    - Use Python 3.12+ syntax
    - Add type hints to all functions
    - Include docstrings
    - Handle edge cases gracefully

  ...

============================================================
Step 7: Running the Evaluation
============================================================

  Command: harbor run -p tasks/code-task -a agent:TemplatedAgent \
           --agent-kwarg prompt_template_path=templates/template.md.j2
  ...
  Evaluation completed successfully!
```

## Key Takeaways

- Prompt templates wrap raw instructions with context and guidelines using Jinja2 syntax
- Use `{{ instruction }}` in templates as the placeholder for the raw task instruction
- `@with_prompt_template` decorator auto-renders the template before `run()` executes
- `render_instruction()` does the actual Jinja2 rendering under the hood
- SKILL.md files inject domain knowledge into agents that support skills
- Pass templates via `--agent-kwarg prompt_template_path=<path>` on the CLI or in `job.yaml`
- Templates let you change agent behavior without modifying task instruction files

## Next Steps

Next lesson: **agent-with-llm** -- Build agents powered by language models
