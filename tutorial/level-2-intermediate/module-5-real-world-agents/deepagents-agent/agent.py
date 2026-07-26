"""
Deepagents framework agent wrapped as a Harbor BaseAgent.

Deepagents (by LangChain) provides a higher-level agent framework
built on LangGraph with built-in middleware for filesystem operations,
memory, subagents, and more. This wrapper bridges Deepagents into
Harbor's evaluation pipeline.
"""

import asyncio
from typing import Any

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool as langchain_tool
from langchain_openai import ChatOpenAI

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext


class DeepagentsHarborAgent(BaseAgent):
    """A Deepagents-based agent wrapped as a Harbor BaseAgent.

    Deepagents provides create_deep_agent() which builds a LangGraph
    agent with middleware for planning, filesystem, memory, and more.

    For Harbor integration, we use a simplified approach: we create
    a Deepagents-style agent with an execute_command tool that bridges
    to Harbor's environment.exec(). The agent uses the same LLM loop
    pattern that Deepagents uses internally, but routes all operations
    through Harbor's container environment.
    """

    @staticmethod
    def name() -> str:
        return "deepagents-agent"

    def version(self) -> str | None:
        return "0.1.0"

    async def setup(self, environment: BaseEnvironment) -> None:
        pass

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """Run the Deepagents-style agent to complete the task.

        We use Deepagents' create_deep_agent() to build a graph with
        built-in middleware, then execute it with a tool that bridges
        to Harbor's environment.
        """
        loop = asyncio.get_running_loop()

        def run_async_in_thread(coro: Any) -> Any:
            future = asyncio.run_coroutine_threadsafe(coro, loop)
            return future.result(timeout=120)

        @langchain_tool
        def execute_command(command: str) -> str:
            """Execute a shell command in the task environment container.

            Use this to run bash commands, create files and directories,
            install packages, run scripts, and verify your work.
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

        @langchain_tool
        def write_file(path: str, content: str) -> str:
            """Write content to a file in the task environment.

            Args:
                path: Absolute path to the file to create/overwrite.
                content: The content to write to the file.
            """
            # Escape content for shell heredoc
            escaped = content.replace("'", "'\\''")
            cmd = f"mkdir -p $(dirname '{path}') && cat << 'HARBEOF' > '{path}'\n{content}\nHARBEOF"
            result = run_async_in_thread(environment.exec(command=cmd))
            if hasattr(result, "return_code") and result.return_code != 0:
                stderr = getattr(result, "stderr", "") or ""
                return f"Error writing file: {stderr}"
            return f"Successfully wrote {path}"

        @langchain_tool
        def read_file(path: str) -> str:
            """Read the contents of a file in the task environment.

            Args:
                path: Absolute path to the file to read.
            """
            result = run_async_in_thread(
                environment.exec(command=f"cat '{path}'")
            )
            if hasattr(result, "stdout") and result.stdout:
                return result.stdout
            stderr = getattr(result, "stderr", "") or ""
            return f"Error reading file: {stderr}"

        # Set up LLM
        model_name = self.model_name or "openai/gpt-4o"
        if "/" in model_name:
            model_name = model_name.split("/", 1)[1]

        llm = ChatOpenAI(model=model_name)

        # Try to use Deepagents' create_deep_agent if available
        try:
            from deepagents import create_deep_agent

            tools = [execute_command, write_file, read_file]
            agent = create_deep_agent(
                model=llm,
                tools=tools,
                prompt=(
                    "You are a coding agent working inside a Docker container. "
                    "Use the provided tools to complete the task."
                ),
            )

            initial_state = {
                "messages": [HumanMessage(content=instruction)],
            }

            await asyncio.to_thread(
                agent.invoke,
                initial_state,
                {"recursion_limit": 30},
            )

        except (ImportError, Exception) as e:
            # Fallback: manual agent loop (Deepagents-style pattern)
            self.logger.info(
                f"Using fallback agent loop (Deepagents import: {e})"
            )
            tools = [execute_command, write_file, read_file]
            llm_with_tools = llm.bind_tools(tools)
            tool_map = {t.name: t for t in tools}

            from langchain_core.messages import AIMessage, ToolMessage

            messages: list[Any] = [
                HumanMessage(content=(
                    "You are a coding agent working inside a Docker container. "
                    "You have tools for executing commands, writing files, and "
                    "reading files. Complete the following task:\n\n"
                    f"{instruction}"
                ))
            ]

            for _ in range(20):
                response = await asyncio.to_thread(
                    llm_with_tools.invoke, messages
                )
                messages.append(response)

                if not response.tool_calls:
                    break

                for tc in response.tool_calls:
                    fn = tool_map.get(tc["name"])
                    if fn:
                        result = fn.invoke(tc["args"])
                    else:
                        result = f"Unknown tool: {tc['name']}"
                    messages.append(
                        ToolMessage(content=result, tool_call_id=tc["id"])
                    )
