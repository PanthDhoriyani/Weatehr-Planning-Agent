"""
graph.py — AgriShield AI: Multi-Agent Graph with Reflection Critic
------------------------------------------------------------------
Architecture:
  START ──► [Supervisor Node]
                  │
                  ▼
              [LLM Node] ──(has tool calls?)──► [Tool Node (Open-Meteo Agri API)]
                  │                                         │
                  ▼ (no tool / refusal)                     ▼
                 END                        [Sub-Agent Dispatch Node]
                                                    │
                                                    ▼
                                          [Critic & Reflection Node]
                                                    │
                                                    ▼
                                                   END

Highlights:
- Unit 3: Long-term Farm Profile Memory injected in LLM Node & persisted by Critic Node.
- Unit 4: Supervisor routes to 3 domain specialists (Irrigation, Pest/Disease, Harvest/Spray).
- Final Jury Innovation: Evaluator-Optimizer / Reflection Loop via Critic Node.
"""

from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import (
    supervisor_node,
    llm_node,
    tool_node,
    sub_agent_dispatch_node,
    critic_node,
)


def should_continue(state: AgentState):
    """
    Evaluates whether the LLM invoked the agricultural telemetry tool.
    - If tool call present → proceed to tool_node.
    - If off-topic or direct response → terminate at END.
    """
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


def build_graph():
    """Builds and compiles the AgriShield LangGraph multi-agent graph."""
    graph = StateGraph(AgentState)

    # ── Graph Nodes ──────────────────────────────────────────────
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("llm", llm_node)
    graph.add_node("tools", tool_node)
    graph.add_node("sub_agent", sub_agent_dispatch_node)
    graph.add_node("critic", critic_node)

    # ── Graph Edges & Flow ───────────────────────────────────────
    graph.set_entry_point("supervisor")
    graph.add_edge("supervisor", "llm")

    graph.add_conditional_edges(
        "llm",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )

    graph.add_edge("tools", "sub_agent")
    graph.add_edge("sub_agent", "critic")
    graph.add_edge("critic", END)

    return graph.compile()
