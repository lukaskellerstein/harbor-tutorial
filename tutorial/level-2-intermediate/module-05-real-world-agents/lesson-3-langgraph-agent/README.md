# Langgraph Agent in Harbor

**Duration:** 45-60 minutes

## Overview

LangGraph adds explicit state management and graph-based control flow on top of the LangChain ecosystem. In Lesson 2, `create_agent()` built the ReAct loop for you — LangGraph is what it builds on. In this lesson you assemble that graph yourself with **LangGraph 1.x**'s `StateGraph`, wrap it as a Harbor `BaseAgent`, and evaluate it on a multi-step reasoning task. The model is served by the LiteLLM proxy (Gemma 4).

## Prerequisites

- Completed Lesson 2 (LangChain Agent in Harbor)
- Docker installed and running
- Harbor CLI installed
- The LiteLLM gateway from `agent-eval-benchmark/infra` running:

  ```bash
  cd agent-eval-benchmark/infra && podman compose up -d
  # for the local model aliases: lms server start && lms load google/gemma-4-e4b
  ```

  The gateway serves Gemma 4 under friendly aliases (see `infra/litellm/config.yaml`):
  `gemma-large` (26B, used here), `gemma-small` / `gemma-local` (4B via LMStudio).
  No provider API key is needed in this lesson — the proxy holds the keys.

## Concepts

### StateGraph vs `create_agent()`

`create_agent()` returns a compiled graph with the ReAct loop already wired. Dropping to `StateGraph` means writing those nodes and edges yourself — more code, in exchange for control over every hop:

```
[START] -> [chatbot] --(has tool calls)--> [tools]
               ^                              |
               |______________________________|
               |
        (no tool calls)
               |
             [END]
```

### Graph Components

- **State** -- a `TypedDict` defining the data flowing through the graph (messages)
- **Reducer** -- `Annotated[list[AnyMessage], add_messages]` makes returned messages *append* to history instead of replacing it; that accumulation is what makes the loop stateful
- **Nodes** -- functions that receive and transform state (chatbot node, tools node)
- **Edges** -- connections between nodes, including conditional edges that route based on state
- **ToolNode** -- a prebuilt LangGraph node that executes tool calls from AI messages
- **`tools_condition`** -- the prebuilt router that inspects the last message and returns `"tools"` or `END`

### LangGraph 1.x Idioms

Older tutorials (LangGraph 0.x) show `set_entry_point()` and a hand-written `should_continue()`. The current equivalents:

```python
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

graph.add_edge(START, "chatbot")                     # was set_entry_point("chatbot")
graph.add_conditional_edges(
    "chatbot", tools_condition, {"tools": "tools", END: END}
)                                                    # was a custom should_continue()
```

### Async All the Way Down

Harbor's `environment.exec()` is `async`, so the tool, the chatbot node, and the graph run are all async:

```python
@tool
async def execute_command(command: str) -> str:
    """Execute a shell command in the task container."""
    result = await environment.exec(command=command, timeout_sec=300)
    parts = [p for p in (result.stdout, result.stderr) if p]
    return "\n".join(parts) or "(no output)"

async def chatbot(state: AgentState) -> dict[str, list[AnyMessage]]:
    response = await llm_with_tools.ainvoke(state["messages"])
    return {"messages": [response]}

await compiled.ainvoke(initial_state, {"recursion_limit": 50})
```

Note what is *absent*: no `asyncio.run_coroutine_threadsafe`, no `asyncio.to_thread`, no worker threads. `ainvoke()` runs async nodes and tools on Harbor's own event loop. Reach for thread bridging only when a framework gives you no async path.

### Models via the LiteLLM Proxy

The agent builds a `ChatOpenAI` client pointed at the gateway:

```python
llm = ChatOpenAI(
    model="gemma-large",                      # alias in infra/litellm/config.yaml
    base_url=os.environ.get("LITELLM_BASE_URL", "http://localhost:4000/v1"),
    api_key=os.environ.get("LITELLM_API_KEY", "sk-litellm-master"),
    temperature=0.0,
)
llm_with_tools = llm.bind_tools(tools)
```

Switching provider or model is a config change in `infra/litellm/config.yaml`, never a code change here. The `-m` flag still works: `harbor run ... -m gemma-small` routes to the local 4B model.

### Why Graphs Matter for Evaluation

The graph structure makes it straightforward to:
- Add planning nodes before execution
- Add reflection/verification nodes after tool execution
- Implement retry logic with backtracking
- Set recursion limits to prevent runaway agents

## Step-by-Step

### Step 1: Understand the Agent Graph

The `agent.py` file builds a two-node graph:

```python
graph = StateGraph(AgentState)
graph.add_node("chatbot", chatbot)       # LLM reasoning
graph.add_node("tools", ToolNode(tools)) # Tool execution
graph.add_edge(START, "chatbot")
graph.add_conditional_edges("chatbot", tools_condition, {"tools": "tools", END: END})
graph.add_edge("tools", "chatbot")
compiled = graph.compile()
```

### Step 2: Examine the Multi-Step Task

The task requires four sequential steps: create a directory, write a config file, write a Python script that reads the config, and run the script. This tests the agent's ability to maintain state across multiple tool calls — exactly what the `add_messages` reducer accumulates.

### Step 3: Run the Evaluation

```bash
cd tutorial/level-2-intermediate/module-05-real-world-agents/lesson-3-langgraph-agent
uv sync
uv run python main.py
```

`main.py` sets `PYTHONPATH` to the lesson directory so the `harbor` subprocess can import `agent`. To run it directly:

```bash
PYTHONPATH=. harbor run -p tasks/multi-step-task --agent agent:LanggraphHarborAgent -m gemma-large
```

## Expected Output

```
Step 2: LangGraph vs create_agent()
  StateGraph components:
    - State: TypedDict defining the data flowing through the graph
    - Nodes: Functions that transform state (chatbot, tools)
    - Edges: Connections between nodes (including conditional)
  ...

Step 4: Running Evaluation
  Running: harbor run -p tasks/multi-step-task --agent agent:LanggraphHarborAgent -m gemma-large
  ...

Step 5: Results
  Task: tutorial/multi-step-task
  Reward: 1.0
```

## Key Takeaways

- LangGraph uses an explicit `StateGraph` with nodes and edges instead of an implicit loop
- The `add_messages` reducer accumulates history — that is what makes the graph stateful
- `ToolNode` and `tools_condition` are prebuilt components; you rarely hand-write either
- LangGraph 1.x uses `add_edge(START, ...)` rather than `set_entry_point()`
- Async nodes and tools run on Harbor's event loop via `ainvoke()` — no thread bridging
- All model traffic goes through the LiteLLM proxy under the `gemma-large` (Gemma 4) alias
- Multi-step tasks are ideal for testing stateful agent reasoning

## Next Steps

In the next lesson, you will wrap a Deepagents framework agent, which provides built-in filesystem tools and subagent orchestration.
