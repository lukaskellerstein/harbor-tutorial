"""
LangGraph agent wrapped as a Harbor BaseAgent.

Lesson 2 used LangChain v1's create_agent(), which builds the ReAct loop for
you. Here we drop one level down and build that graph by hand with LangGraph
1.x's StateGraph — explicit state, nodes, and edges:

    START -> chatbot --(tool calls)--> tools -> chatbot -> ... -> END

Everything is async: the tool awaits Harbor's environment.exec() directly, the
chatbot node awaits the model, and the graph runs via ainvoke(). No worker
threads, no asyncio.run_coroutine_threadsafe bridging.

The model is served by the LiteLLM proxy (see agent-eval-benchmark/infra/
litellm/config.yaml) using the `gemma-large` alias (Gemma 4 26B).
"""

import os
from typing import Annotated, TypedDict

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import SecretStr

# Alias defined in agent-eval-benchmark/infra/litellm/config.yaml (Gemma 4 26B).
DEFAULT_MODEL = "gemma-large"
EXEC_TIMEOUT_SEC = 300
# One graph step is one node execution, so a chatbot -> tools round trip costs
# two. This bounds a model that never stops calling tools.
RECURSION_LIMIT = 50

SYSTEM_PROMPT = (
    "You are a coding agent working inside a Docker container. "
    "Use the execute_command tool to run shell commands and complete the "
    "task. All paths are inside the container. Work through the steps in "
    "order and verify each one before moving on."
)


class AgentState(TypedDict):
    """State schema for the graph.

    `add_messages` is a reducer: when a node returns {"messages": [...]},
    LangGraph appends to the existing list instead of replacing it. That
    accumulating history is what makes the loop stateful.
    """

    messages: Annotated[list[AnyMessage], add_messages]


class LanggraphHarborAgent(BaseAgent):
    """A LangGraph StateGraph agent wrapped as a Harbor BaseAgent.

    The graph has two nodes:
      - chatbot: calls the LLM, which has the tools bound to it
      - tools:   executes any tool calls the LLM emitted (prebuilt ToolNode)

    A conditional edge routes chatbot -> tools while the LLM keeps calling
    tools, and chatbot -> END on the first reply without any.
    """

    @staticmethod
    def name() -> str:
        return "langgraph-agent"

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
        """Build the graph and run it until the LLM stops calling tools."""

        @tool
        async def execute_command(command: str) -> str:
            """Execute a shell command in the task environment container.

            Use this to run bash commands, create files and directories,
            install packages, and verify your work.
            """
            result = await environment.exec(command=command, timeout_sec=EXEC_TIMEOUT_SEC)
            parts = [p for p in (result.stdout, result.stderr) if p]
            return "\n".join(parts) or "(no output)"

        tools = [execute_command]

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
        llm_with_tools = llm.bind_tools(tools)

        async def chatbot(state: AgentState) -> dict[str, list[AnyMessage]]:
            """Call the LLM with the accumulated message history."""
            response = await llm_with_tools.ainvoke(state["messages"])
            return {"messages": [response]}

        graph = StateGraph(AgentState)
        graph.add_node("chatbot", chatbot)
        graph.add_node("tools", ToolNode(tools))

        graph.add_edge(START, "chatbot")
        # tools_condition is LangGraph's prebuilt router: it inspects the last
        # message and returns "tools" if it carries tool calls, else END.
        graph.add_conditional_edges("chatbot", tools_condition, {"tools": "tools", END: END})
        graph.add_edge("tools", "chatbot")

        compiled = graph.compile()

        # ainvoke keeps the async tool on Harbor's event loop.
        await compiled.ainvoke(
            {
                "messages": [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=instruction),
                ]
            },
            {"recursion_limit": RECURSION_LIMIT},
        )
