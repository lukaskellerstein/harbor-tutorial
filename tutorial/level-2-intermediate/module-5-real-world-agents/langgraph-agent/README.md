# Langgraph Agent in Harbor

**Duration:** 45-60 minutes

## Overview

LangGraph adds explicit state management and graph-based control flow on top of the Langchain ecosystem. In this lesson, you will build a LangGraph `StateGraph` agent, wrap it as a Harbor `BaseAgent`, and evaluate it on a multi-step reasoning task.

## Prerequisites

- Completed Lesson 2 (Langchain Agent in Harbor)
- Docker installed and running
- Harbor CLI installed
- `OPENAI_API_KEY` environment variable set

## Concepts

### StateGraph vs Simple Loops

In Lesson 2, you used a while-loop to alternate between LLM calls and tool execution. LangGraph replaces this with an explicit directed graph:

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
- **Nodes** -- functions that receive and transform state (chatbot node, tools node)
- **Edges** -- connections between nodes, including conditional edges that route based on state
- **ToolNode** -- a pre-built LangGraph node that executes tool calls from AI messages

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
graph.set_entry_point("chatbot")
graph.add_conditional_edges("chatbot", should_continue, ...)
graph.add_edge("tools", "chatbot")
```

### Step 2: Examine the Multi-Step Task

The task requires four sequential steps: create a directory, write a config file, write a Python script that reads the config, and run the script. This tests the agent's ability to maintain state across multiple tool calls.

### Step 3: Run the Evaluation

```bash
cd tutorial/level-2-intermediate/module-5-real-world-agents/langgraph-agent
uv sync
export OPENAI_API_KEY=sk-...
uv run python main.py
```

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-5-real-world-agents/langgraph-agent
uv sync
export OPENAI_API_KEY=sk-...
uv run python main.py
```

## Expected Output

```
Step 2: LangGraph vs Langchain Agent Patterns
  StateGraph components:
    - State: TypedDict defining the data flowing through the graph
    - Nodes: Functions that transform state (chatbot, tools)
    - Edges: Connections between nodes (including conditional)
  ...

Step 4: Running Evaluation
  ...

Step 5: Results
  Task: tutorial/multi-step-task
  Reward: 1.0
```

## Key Takeaways

- LangGraph uses explicit `StateGraph` with nodes and edges instead of implicit loops
- The `ToolNode` pre-built component handles tool call execution automatically
- Conditional edges route between tool execution and completion
- The graph pattern makes it easy to add planning, reflection, and retry nodes
- Multi-step tasks are ideal for testing stateful agent reasoning

## Next Steps

In the next lesson, you will wrap a Deepagents framework agent, which provides built-in filesystem tools and subagent orchestration.
