"""
Lesson 3: Prompt Templates

Learn how prompt templates structure and enhance the instructions
given to Harbor agents using Jinja2 templates and SKILL.md files.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from jinja2 import Environment

LESSON_DIR = Path(__file__).parent


def check_prerequisites() -> bool:
    """Verify Docker and Harbor are available."""
    print("=" * 60)
    print("Step 0: Checking Prerequisites")
    print("=" * 60)
    print()

    docker_ok = shutil.which("docker") is not None
    harbor_ok = shutil.which("harbor") is not None

    if docker_ok:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            check=False,
        )
        docker_ok = result.returncode == 0

    print(f"  Docker installed and running: {'[OK]' if docker_ok else '[FAIL]'}")
    print(f"  Harbor CLI installed:         {'[OK]' if harbor_ok else '[FAIL]'}")
    print()

    if not docker_ok:
        print("  Docker must be installed and running. Start Docker Desktop.")
    if not harbor_ok:
        print("  Install Harbor: uv tool install harbor")

    return docker_ok and harbor_ok


def explain_prompt_templates() -> None:
    """Step 1: Explain what prompt templates are and why they matter."""
    print("=" * 60)
    print("Step 1: What Are Prompt Templates?")
    print("=" * 60)
    print()
    print("  Prompt templates are Jinja2 templates that WRAP the raw task")
    print("  instruction before it reaches your agent's run() method.")
    print()
    print("  Why they matter:")
    print("    - Consistent formatting across all tasks")
    print("    - Add system prompts and guidelines without modifying tasks")
    print("    - Inject coding standards, safety rules, or personas")
    print("    - Separate task content from agent behavior instructions")
    print()
    print("  How they work:")
    print("    1. You write a Jinja2 template with {{ instruction }}")
    print("    2. Harbor reads the raw instruction from instruction.md")
    print("    3. The template engine replaces {{ instruction }} with the")
    print("       raw instruction text")
    print("    4. Your agent receives the fully rendered prompt")
    print()


def show_template_file() -> None:
    """Step 2: Show the template file contents."""
    print("=" * 60)
    print("Step 2: The Template File")
    print("=" * 60)
    print()

    template_file = LESSON_DIR / "templates" / "template.md.j2"
    if template_file.exists():
        print("  File: templates/template.md.j2")
        print()
        for line in template_file.read_text().strip().splitlines():
            print(f"    {line}")
    else:
        print("  [ERROR] templates/template.md.j2 not found!")
    print()
    print("  The {{ instruction }} placeholder is the key -- it gets")
    print("  replaced with the raw task instruction at render time.")
    print()


def demonstrate_rendering() -> None:
    """Step 3: Show template rendering in action."""
    print("=" * 60)
    print("Step 3: Template Rendering Demo")
    print("=" * 60)
    print()

    template_file = LESSON_DIR / "templates" / "template.md.j2"
    template_content = template_file.read_text()

    raw_instruction = "Write a Python function that adds two numbers."

    print("  RAW INSTRUCTION:")
    print(f"    {raw_instruction}")
    print()

    # Render using Jinja2
    env = Environment()
    template = env.from_string(template_content)
    rendered = template.render(instruction=raw_instruction)

    print("  RENDERED (after template):")
    print("  " + "-" * 50)
    for line in rendered.strip().splitlines():
        print(f"    {line}")
    print("  " + "-" * 50)
    print()
    print("  Notice how the raw instruction is now wrapped with system")
    print("  context, rules, and guidelines from the template.")
    print()


def explain_decorator() -> None:
    """Step 4: Explain the @with_prompt_template decorator."""
    print("=" * 60)
    print("Step 4: The @with_prompt_template Decorator")
    print("=" * 60)
    print()
    print("  The decorator automates template rendering for installed agents:")
    print()
    print("    @with_prompt_template")
    print("    async def run(self, instruction, environment, context):")
    print("        # 'instruction' is already rendered through the template!")
    print("        ...")
    print()
    print("  What happens under the hood:")
    print("    1. Before run() executes, the decorator intercepts the call")
    print("    2. It calls self.render_instruction(instruction)")
    print("    3. render_instruction() loads the Jinja2 template file")
    print("    4. It renders {{ instruction }} with the raw instruction")
    print("    5. The rendered result replaces the instruction parameter")
    print("    6. Your run() method receives the fully rendered prompt")
    print()
    print("  The template path is set via prompt_template_path kwarg when")
    print("  the agent is instantiated (passed through job.yaml config or")
    print("  --agent-kwarg on the CLI).")
    print()


def explain_skills() -> None:
    """Step 5: Explain SKILL.md files."""
    print("=" * 60)
    print("Step 5: SKILL.md Files")
    print("=" * 60)
    print()
    print("  Skills are markdown files that provide domain knowledge to agents.")
    print()
    print("  Structure:")
    print("    skills/")
    print("      solve-task/")
    print("        SKILL.md    # Domain knowledge for the agent")
    print()
    print("  How they work:")
    print("    - Agents that support skills load SKILL.md during setup")
    print("    - The skill content is injected into the agent's context")
    print("    - This gives the agent domain-specific guidelines")
    print()

    skill_file = LESSON_DIR / "skills" / "solve-task" / "SKILL.md"
    if skill_file.exists():
        print("  Our sample skill (skills/solve-task/SKILL.md):")
        print("  " + "-" * 50)
        for line in skill_file.read_text().strip().splitlines():
            print(f"    {line}")
        print("  " + "-" * 50)
    else:
        print("  [ERROR] skills/solve-task/SKILL.md not found!")
    print()


def show_agent_code() -> None:
    """Step 6: Show the TemplatedAgent implementation."""
    print("=" * 60)
    print("Step 6: The TemplatedAgent Implementation")
    print("=" * 60)
    print()

    agent_file = LESSON_DIR / "agent.py"
    if agent_file.exists():
        code = agent_file.read_text()
        print(code)
    else:
        print("  [ERROR] agent.py not found!")
    print()


def run_evaluation() -> None:
    """Step 7: Run the evaluation with the templated agent."""
    print("=" * 60)
    print("Step 7: Running the Evaluation")
    print("=" * 60)
    print()

    task_path = LESSON_DIR / "tasks" / "code-task"
    template_path = LESSON_DIR / "templates" / "template.md.j2"

    cmd = [
        "harbor",
        "run",
        "-p",
        str(task_path),
        "-a",
        "agent:TemplatedAgent",
        "--agent-kwarg",
        f"prompt_template_path={template_path}",
    ]

    print("  Command: harbor run -p tasks/code-task -a agent:TemplatedAgent \\")
    print("           --agent-kwarg prompt_template_path=templates/template.md.j2")
    print()
    print("  What will happen:")
    print("    1. Harbor builds the Docker container (python:3.12-slim)")
    print("    2. setup() calls install() -- verifies Python is available")
    print("    3. @with_prompt_template renders the instruction through")
    print("       templates/template.md.j2 before run() executes")
    print("    4. run() creates fibonacci.py inside the container")
    print("    5. The verifier checks that fibonacci.py produces correct output")
    print()
    print("-" * 60)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(LESSON_DIR),
        check=False,
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    print("-" * 60)

    if result.returncode == 0:
        print("\n  Evaluation completed successfully!")
    else:
        print(f"\n  Evaluation failed (exit code {result.returncode}).")
        print("  Make sure Docker is running and try again.")
    print()

    # Show results if available
    jobs_dir = LESSON_DIR / "jobs"
    if jobs_dir.exists():
        result_files = sorted(jobs_dir.rglob("result.json"))
        if result_files:
            latest = result_files[-1]
            print(f"  Latest result: {latest.name}")
            print(f"  {latest.read_text().strip()}")
            print()


def show_summary() -> None:
    """Print key takeaways."""
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("  You learned how prompt templates structure agent instructions:")
    print()
    print("  Key takeaways:")
    print("    - Prompt templates are Jinja2 files with {{ instruction }}")
    print("    - They wrap raw task instructions with context and guidelines")
    print("    - @with_prompt_template auto-renders before run() executes")
    print("    - render_instruction() does the actual Jinja2 rendering")
    print("    - Templates are passed via prompt_template_path kwarg")
    print("    - SKILL.md files inject domain knowledge into agents")
    print("    - Templates let you change agent behavior without editing tasks")
    print()
    print("  Next lesson: lesson-4-agent-with-llm")
    print("    Build agents powered by language models")
    print()


def main() -> None:
    """Run the prompt-templates lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Module 4, Lesson 3         #")
    print("#     Prompt Templates                                  #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_prompt_templates()
    show_template_file()
    demonstrate_rendering()
    explain_decorator()
    explain_skills()
    show_agent_code()
    run_evaluation()
    show_summary()


if __name__ == "__main__":
    main()
