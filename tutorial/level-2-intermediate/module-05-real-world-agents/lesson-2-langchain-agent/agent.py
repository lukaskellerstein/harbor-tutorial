"""
LangChain agent wrapped as a Harbor BaseAgent.

Built on LangChain v1's create_agent() — the standard way to build a
ReAct-style agent. It runs the reason -> call tools -> observe loop for us
on top of LangGraph, so there is no hand-written iteration loop here.

Two things make this wrapper short:

  1. create_agent() owns the agent loop. We supply a model, a tool, and a
     system prompt; it handles tool dispatch, message accumulation, and
     termination.
  2. LangChain tools can be `async def`. The tool awaits Harbor's
     environment.exec() directly — no thread/event-loop bridging.

The model is served by the LiteLLM proxy (see agent-eval-benchmark/infra/
litellm/config.yaml) using the `gemma-large` alias (Gemma 4 26B).
"""

import os

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

# Alias defined in agent-eval-benchmark/infra/litellm/config.yaml (Gemma 4 26B).
DEFAULT_MODEL = "gemma-large"
EXEC_TIMEOUT_SEC = 300
# Each agent step is one model call; a step that calls a tool costs two.
RECURSION_LIMIT = 50

SYSTEM_PROMPT = (
    "You are a coding agent working inside a Docker container. "
    "Use the execute_command tool to run shell commands and complete the "
    "task. All paths are inside the container. Verify your work by running "
    "the relevant commands before you finish."
)


class LangchainHarborAgent(BaseAgent):
    """A LangChain create_agent() agent wrapped as a Harbor BaseAgent.

    The single tool bridges the LLM to the task container: everything the
    agent does to the environment goes through environment.exec().
    """

    @staticmethod
    def name() -> str:
        return "langchain-agent"

    def version(self) -> str | None:
        return "0.2.0"

    async def setup(self, environment: BaseEnvironment) -> None:
        """No setup needed — the agent runs on the host, not in the container."""

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """Build the agent and run it until it stops calling tools."""

        @tool
        async def execute_command(command: str) -> str:
            """Execute a shell command in the task environment container.

            Use this to run bash commands, create files, install packages,
            and verify your work. The command runs inside a Docker container
            with the task's environment.
            """
            result = await environment.exec(command=command, timeout_sec=EXEC_TIMEOUT_SEC)
            parts = [p for p in (result.stdout, result.stderr) if p]
            return "\n".join(parts) or "(no output)"

        # The -m flag lands in self.model_name. Accept both a bare LiteLLM
        # alias ("gemma-large") and a provider-prefixed form ("openai/gemma-large").
        model_name = self.model_name or DEFAULT_MODEL
        if "/" in model_name:
            model_name = model_name.split("/", 1)[1]

        llm = ChatOpenAI(
            model=model_name,
            base_url=os.environ.get("LITELLM_BASE_URL", "http://localhost:4000/v1"),
            api_key=SecretStr(os.environ.get("LITELLM_API_KEY", "sk-litellm-master")),
            temperature=0.0,
        )

        agent = create_agent(
            model=llm,
            tools=[execute_command],
            system_prompt=SYSTEM_PROMPT,
        )

        # ainvoke keeps the async tool on Harbor's event loop.
        await agent.ainvoke(
            {"messages": [HumanMessage(content=instruction)]},
            {"recursion_limit": RECURSION_LIMIT},
        )
