"""
Langchain Agent wrapped as a Harbor BaseAgent.

The key challenge: Langchain tools are synchronous, but Harbor's
environment.exec() is async. We bridge this gap using a thread-safe
approach with asyncio event loops.
"""

import asyncio
from typing import Any

from langchain_core.tools import tool as langchain_tool
from langchain_openai import ChatOpenAI

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext


class LangchainHarborAgent(BaseAgent):
    """A Langchain ReAct agent wrapped as a Harbor BaseAgent.

    This agent creates a Langchain tool that bridges to Harbor's
    async environment.exec() method, allowing the LLM to execute
    commands inside the task container.
    """

    @staticmethod
    def name() -> str:
        return "langchain-agent"

    def version(self) -> str | None:
        return "0.1.0"

    async def setup(self, environment: BaseEnvironment) -> None:
        """No special setup needed for an external agent."""
        pass

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """Run the Langchain agent to complete the task."""
        # We need a separate event loop for running async Harbor calls
        # from within synchronous Langchain tool callbacks.
        # This is the fundamental challenge of bridging sync and async worlds.
        loop = asyncio.get_running_loop()

        def run_async_in_thread(coro: Any) -> Any:
            """Run an async coroutine from a sync context by scheduling
            it on the running event loop from a worker thread."""
            future = asyncio.run_coroutine_threadsafe(coro, loop)
            return future.result(timeout=120)

        @langchain_tool
        def execute_command(command: str) -> str:
            """Execute a shell command in the task environment container.

            Use this to run bash commands, create files, install packages,
            and verify your work. The command runs inside a Docker container
            with the task's environment.
            """
            result = run_async_in_thread(environment.exec(command=command))
            output = ""
            if hasattr(result, "stdout") and result.stdout:
                output += result.stdout
            if hasattr(result, "stderr") and result.stderr:
                if output:
                    output += "\n"
                output += result.stderr
            return output or "(no output)"

        # Create the LLM — uses OPENAI_API_KEY from the environment
        model_name = self.model_name or "openai/gpt-4o"
        # Strip provider prefix for OpenAI client
        if "/" in model_name:
            model_name = model_name.split("/", 1)[1]

        llm = ChatOpenAI(model=model_name)

        # Bind tools to the LLM and create a simple agent loop
        tools = [execute_command]
        llm_with_tools = llm.bind_tools(tools)

        # Build the messages
        from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

        messages = [
            HumanMessage(content=(
                "You are a coding agent working inside a Docker container. "
                "Use the execute_command tool to run shell commands and complete the task.\n\n"
                f"TASK:\n{instruction}"
            ))
        ]

        # Simple agent loop: call LLM, execute tools, repeat
        max_iterations = 15
        for i in range(max_iterations):
            # Call the LLM (run sync langchain in a thread to not block)
            response = await asyncio.to_thread(llm_with_tools.invoke, messages)
            messages.append(response)

            # Check if the LLM made tool calls
            if not response.tool_calls:
                # No more tool calls — agent is done
                break

            # Execute each tool call
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                if tool_name == "execute_command":
                    result = execute_command.invoke(tool_args)
                else:
                    result = f"Unknown tool: {tool_name}"

                messages.append(
                    ToolMessage(content=result, tool_call_id=tool_call["id"])
                )
