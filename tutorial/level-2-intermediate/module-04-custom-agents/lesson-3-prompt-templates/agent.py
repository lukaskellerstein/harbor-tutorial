"""
Lesson 3: Templated Agent -- Demonstrates prompt template usage.

This agent uses @with_prompt_template to wrap the raw task instruction
with structured guidelines before processing it.
"""

from harbor.agents.installed.base import BaseInstalledAgent, with_prompt_template
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext


class TemplatedAgent(BaseInstalledAgent):
    """An agent that uses prompt templates to structure its instructions.

    The @with_prompt_template decorator on run() automatically renders
    the raw instruction through the configured Jinja2 template before
    the method body executes.
    """

    @staticmethod
    def name() -> str:
        return "templated-agent"

    async def install(self, environment: BaseEnvironment) -> None:
        """Minimal install -- Python is already available in the container."""
        await self.exec_as_agent(environment, command="python3 --version")

    @with_prompt_template
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """Run the agent with a template-rendered instruction.

        By the time this method executes, the 'instruction' parameter
        has already been rendered through the Jinja2 prompt template.
        The raw task instruction has been wrapped with the template's
        system prompt, guidelines, and formatting.
        """
        self.logger.info(f"Received rendered instruction ({len(instruction)} chars)")

        # The instruction now includes the template wrapper.
        # For this demo agent, we create the fibonacci solution directly.
        # A real LLM-powered agent would send this rendered instruction
        # to an LLM and use the response to solve the task.

        fibonacci_code = '''def fibonacci(n: int) -> list[int]:
    """Return the first n Fibonacci numbers."""
    if n <= 0:
        return []
    if n == 1:
        return [0]
    fibs = [0, 1]
    for _ in range(2, n):
        fibs.append(fibs[-1] + fibs[-2])
    return fibs

print(fibonacci(10))
'''

        # Write the solution file
        await self.exec_as_agent(
            environment,
            command=f"cat > /home/user/fibonacci.py << 'PYEOF'\n{fibonacci_code}PYEOF",
        )
        self.logger.info("Created /home/user/fibonacci.py")

        # Verify it runs correctly
        result = await self.exec_as_agent(environment, command="python3 /home/user/fibonacci.py")
        self.logger.info(f"Script output: {result.stdout.strip()}")

        # Store metadata
        context.metadata = {
            "instruction_length": len(instruction),
            "template_applied": True,
        }
