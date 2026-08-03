"""
Lesson 4: LLM-Powered Agent — Uses a language model to reason about tasks.

This agent demonstrates the agent-LLM-environment loop:
1. Send instruction to LLM
2. Extract commands from LLM response
3. Execute commands in the environment
4. Check results and retry if needed

The model is served by the LiteLLM proxy (see agent-eval-benchmark/infra/
litellm/config.yaml) using the `gemma-large` alias (Gemma 4 26B).
"""

import os
import re

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext
from litellm import acompletion
from litellm.types.utils import Choices, ModelResponse

# System prompt that tells the LLM how to format its responses
SYSTEM_PROMPT = """You are a coding agent that solves tasks inside a Linux container.
You have access to a Python 3.12 environment.

When given a task, respond with the exact bash commands needed to solve it.
Put your commands inside a ```bash code block.

For example, to create a Python file:
```bash
cat > /home/user/script.py << 'PYEOF'
print("hello")
PYEOF
```

Rules:
- Write complete, working solutions
- Use bash commands (cat, echo, python3, etc.)
- Create files at the exact paths specified in the instruction
- After creating files, verify they work by running them
- If creating a Python script, always test it with python3
"""

MAX_ITERATIONS = 3

# Alias defined in agent-eval-benchmark/infra/litellm/config.yaml (Gemma 4 26B).
DEFAULT_MODEL = "gemma-large"
GATEWAY_BASE_URL = os.environ.get("LITELLM_BASE_URL", "http://localhost:4000/v1")
GATEWAY_API_KEY = os.environ.get("LITELLM_API_KEY", "sk-litellm-master")


def extract_bash_commands(response_text: str) -> list[str]:
    """Extract bash code blocks from LLM response text.

    Looks for ```bash ... ``` blocks and returns the content
    of each block as a separate string.
    """
    pattern = r"```(?:bash|sh)\n(.*?)```"
    matches = re.findall(pattern, response_text, re.DOTALL)

    if not matches:
        # Fallback: try to find any code block
        pattern = r"```\n(.*?)```"
        matches = re.findall(pattern, response_text, re.DOTALL)

    return [m.strip() for m in matches if m.strip()]


class LLMAgent(BaseAgent):
    """An agent that uses an LLM to reason about and solve tasks.

    The agent implements an iterative loop:
    1. Send the task instruction to the LLM
    2. Extract bash commands from the response
    3. Execute commands in the container environment
    4. If execution fails, send the error back to the LLM
    5. Repeat until success or max iterations reached
    """

    @staticmethod
    def name() -> str:
        return "llm-agent"

    def version(self) -> str | None:
        return "0.1.0"

    async def setup(self, environment: BaseEnvironment) -> None:
        """No special setup needed — the agent runs externally."""

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """Run the agent-LLM-environment loop."""

        # The -m flag lands in self.model_name. Accept both a bare LiteLLM
        # alias ("gemma-large") and a provider-prefixed form ("openai/gemma-large").
        model = self.model_name or DEFAULT_MODEL
        alias = model.split("/", 1)[1] if "/" in model else model

        # Build the conversation history
        messages: list[dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": instruction},
        ]

        last_stdout = ""
        last_stderr = ""
        iteration = 0  # so the metadata below is still well-defined if the loop never runs

        for iteration in range(1, MAX_ITERATIONS + 1):
            print(f"\n  [LLMAgent] Iteration {iteration}/{MAX_ITERATIONS}")

            # Step 1: Ask the LLM. The "openai/" prefix tells LiteLLM to treat
            # the proxy as an OpenAI-compatible endpoint; the alias after it is
            # resolved to a real provider by the proxy's config.
            print(f"  [LLMAgent] Sending request to {alias}...")
            response = await acompletion(
                model=f"openai/{alias}",
                api_base=GATEWAY_BASE_URL,
                api_key=GATEWAY_API_KEY,
                messages=messages,
                temperature=0.0,
            )

            # acompletion() can also return a streaming wrapper, and a choice can
            # be a streaming chunk. This call does not stream, so narrow to the
            # non-streaming shapes before reading the text out.
            assert isinstance(response, ModelResponse)
            choice = response.choices[0]
            assert isinstance(choice, Choices)
            assistant_message = choice.message.content or ""

            messages.append({"role": "assistant", "content": assistant_message})
            print(f"  [LLMAgent] Received response ({len(assistant_message)} chars)")

            # Step 2: Extract commands
            commands = extract_bash_commands(assistant_message)
            if not commands:
                print("  [LLMAgent] No bash commands found in response")
                # Ask the LLM to provide commands
                messages.append(
                    {
                        "role": "user",
                        "content": "Please provide the solution as bash commands in a ```bash code block.",
                    }
                )
                continue

            print(f"  [LLMAgent] Extracted {len(commands)} command block(s)")

            # Step 3: Execute each command block
            all_succeeded = True
            for i, cmd in enumerate(commands):
                print(f"  [LLMAgent] Executing command block {i + 1}...")
                result = await environment.exec(command=cmd)
                last_stdout = result.stdout or ""
                last_stderr = result.stderr or ""

                if result.return_code != 0:
                    print(f"  [LLMAgent] Command failed (exit code {result.return_code})")
                    all_succeeded = False

                    # Step 4: Send error back to LLM for next iteration
                    error_msg = (
                        f"Command failed with exit code {result.return_code}.\n"
                        f"stdout: {last_stdout[:500]}\n"
                        f"stderr: {last_stderr[:500]}\n"
                        f"Please fix the issue and provide corrected commands."
                    )
                    messages.append({"role": "user", "content": error_msg})
                    break
                else:
                    print("  [LLMAgent] Command succeeded")
                    if last_stdout.strip():
                        print(f"  [LLMAgent] Output: {last_stdout.strip()[:200]}")

            if all_succeeded:
                print(f"  [LLMAgent] All commands succeeded on iteration {iteration}")
                break
        else:
            print(f"  [LLMAgent] Max iterations ({MAX_ITERATIONS}) reached")

        # Store conversation history in context metadata
        context.metadata = {
            "iterations": min(iteration, MAX_ITERATIONS),
            "model": alias,
            "gateway": GATEWAY_BASE_URL,
            "conversation_length": len(messages),
            "last_stdout": last_stdout[:500],
        }
