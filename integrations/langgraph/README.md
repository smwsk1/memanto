# LangGraph + Memanto Integration

This package provides native LangGraph tools and a standalone memory layer for integrating Memanto's persistent, cross-session memory capabilities into LangGraph agents.

## Installation

```bash
pip install langgraph-memanto
```

## Features

- **Native LangChain Tools**: Easy-to-use `@tool` wrappers that LangGraph agents can autonomously call (`memanto_remember`, `memanto_recall`, `memanto_answer`).
- **Graph Nodes**: Pre-built nodes (`create_recall_node`, `create_remember_node`) for automatic memory injection and storage within your graph.
- **Cross-Session Persistence**: Memories stored by your agents survive across threads, sessions, and even different agents within the same namespace.

## Usage

### Using Tools

```python
from langgraph_memanto import create_memanto_tools
from memanto.cli.client.sdk_client import SdkClient

# Initialize the Memanto SDK Client
client = SdkClient(api_key="your_moorcheh_api_key")

# Get native LangChain tools
# The tools will automatically ensure the agent is created and activated 
# the first time the LLM tries to call them!
tools = create_memanto_tools(client, "my-langgraph-agent")

# Bind them to your LLM
llm_with_tools = llm.bind_tools(tools)
```

### Using Nodes

Add `recall` and `remember` nodes to your graph for automatic memory retrieval before LLM calls and storage after responses.

```python
from langgraph_memanto import create_recall_node, create_remember_node
from memanto.cli.client.sdk_client import SdkClient
from langgraph.graph import StateGraph, MessagesState, START, END

client = SdkClient(api_key="your_moorcheh_api_key")

# Nodes can dynamically use an agent_id from the graph's config
recall = create_recall_node(client=client, agent_id_from_config="agent_id")
remember = create_remember_node(
    client=client,
    agent_id_from_config="agent_id"
)

builder = StateGraph(MessagesState)
builder.add_node("recall", recall)
builder.add_node("agent", agent_node)  # your LLM node
builder.add_node("remember", remember)

builder.add_edge(START, "recall")
builder.add_edge("recall", "agent")
builder.add_edge("agent", "remember")
builder.add_edge("remember", END)

graph = builder.compile()
```
