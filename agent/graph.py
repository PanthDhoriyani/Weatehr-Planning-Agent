"""
graph.py — LangGraph multi-agent graph
----------------------------------------
Original:  START → llm → (tools? → llm)* → END
Extended:
  START → supervisor → llm → (tools? → sub_agent_dispatch)* → END

Unit 3: memory is injected in llm_node
Unit 4: supervisor routes to correct sub-agent via active_agent state field
"""

from langgraph.graph import StateGraph, END

from .state import AgentState
from .nodes import (
    supervisor_node,
    llm_node,
    tool_node,
    sub_agent_dispatch_node,
)


# ---------------------------------------------------------------
# Routing — after LLM node, check if a tool was called
# ---------------------------------------------------------------
def should_continue(state: AgentState):
    """
    After the llm_node runs:
    - If it called a tool → go to tool_node to execute it
    - If no tool call (off-topic refusal or final answer) → END
    """
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# ---------------------------------------------------------------
# Build the extended multi-agent graph
# ---------------------------------------------------------------
def build_graph():
    graph = StateGraph(AgentState)

    # ── Nodes ────────────────────────────────────────────────────
    graph.add_node("supervisor", supervisor_node)    # Unit 4: routing
    graph.add_node("llm", llm_node)                  # Unit 3: memory-aware LLM
    graph.add_node("tools", tool_node)               # tool executor (unchanged)
    graph.add_node("sub_agent", sub_agent_dispatch_node)  # Unit 4: specialist

    # ── Entry Point ──────────────────────────────────────────────
    # Every query goes through supervisor first
    graph.set_entry_point("supervisor")

    # ── Edges ────────────────────────────────────────────────────
    # After supervisor classifies → go to LLM
    graph.add_edge("supervisor", "llm")

    # After LLM: either call tool or end
    graph.add_conditional_edges(
        "llm",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )

    # After tools fetch data → dispatch to the right sub-agent
    # (instead of going back to generic LLM like before)
    graph.add_edge("tools", "sub_agent")

    # Sub-agent gives final answer → END
    graph.add_edge("sub_agent", END)

    return graph.compile()
