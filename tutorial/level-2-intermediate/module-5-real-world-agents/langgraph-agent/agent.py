"""
Langgraph Agent wrapped as a Harbor BaseAgent.

Unlike the simple Langchain agent loop in Lesson 2, this uses
LangGraph's StateGraph to build an explicit graph with nodes and
edges. This enables stateful multi-step reasoning with clear
control flow.
"""

import asyncio
from typing import Annotated, Any, TypedDict

from langchain_core.messages import AnyMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool as langchain_tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext


class AgentState(TypedDict):
    """State schema for the LangGraph agent."""

    messages: Annotated[list[AnyMessage], add_messages]


class LanggraphHarborAgent(BaseAgent):
    """A LangGraph stateful agent wrapped as a Harbor BaseAgent.

    Builds a StateGraph with two nodes:
      - chatbot: calls the LLM with tool bindings
      - tools: executes tool calls via ToolNode

    The graph routes between chatbot and tools until the LLM
    produces a response without tool calls, at which point it ends.
    """

    @staticmethod
    def name() -> str:
        return "langgraph-agent"

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
        """Build and execute the LangGraph agent."""
        loop = asyncio.get_running_loop()

        def run_async_in_thread(coro: Any) -> Any:
            """Schedule an async coroutine on the running loop from sync code."""
            future = asyncio.run_coroutine_threadsafe(coro, loop)
            return future.result(timeout=120)

        @langchain_tool
        def execute_command(command: str) -> str:
            """Execute a shell command in the task environment container.

            Use this to run bash commands, create files and directories,
            install packages, and verify your work.
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

        # Set up the LLM
        model_name = self.model_name or "openai/gpt-4o"
        if "/" in model_name:
            model_name = model_name.split("/", 1)[1]

        llm = ChatOpenAI(model=model_name)
        tools = [execute_command]
        llm_with_tools = llm.bind_tools(tools)

        # Define the graph nodes
        def chatbot(state: AgentState) -> dict[str, list[AnyMessage]]:
            """Call the LLM with the current message history."""
            response = llm_with_tools.invoke(state["messages"])
            return {"messages": [response]}

        def should_continue(state: AgentState) -> str:
            """Determine whether to call tools or end."""
            last_message = state["messages"][-1]
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"
            return END

        # Build the state graph
        graph = StateGraph(AgentState)
        graph.add_node("chatbot", chatbot)
        graph.add_node("tools", ToolNode(tools))

        graph.set_entry_point("chatbot")
        graph.add_conditional_edges("chatbot", should_continue, {"tools": "tools", END: END})
        graph.add_edge("tools", "chatbot")

        compiled = graph.compile()

        # Run the graph
        initial_state: AgentState = {
            "messages": [
                HumanMessage(content=(
                    "You are a coding agent working inside a Docker container. "
                    "Use the execute_command tool to run shell commands and complete the task.\n\n"
                    f"TASK:\n{instruction}"
                ))
            ]
        }

        # Run the synchronous graph in a thread
        final_state = await asyncio.to_thread(
            compiled.invoke,
            initial_state,
            {"recursion_limit": 30},
        )
