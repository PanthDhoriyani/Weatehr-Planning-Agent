from langgraph.graph import StateGraph, END

from .state import AgentState
from .nodes import llm_node, tool_node


# ---------------------------------------------------------------
# Routing function — decides where to go after the LLM node
# ---------------------------------------------------------------
def should_continue(state: AgentState):
    last_message = state["messages"][-1]

    # if the LLM decided to call a tool → go to tool_node
    if last_message.tool_calls:
        return "tools"

    # if no tool call → LLM gave a final answer → end the graph
    return END


# ---------------------------------------------------------------
# Build and compile the LangGraph graph
# ---------------------------------------------------------------
def build_graph():
    # create a new graph that uses AgentState as its state
    graph = StateGraph(AgentState)

    # add nodes to the graph
    graph.add_node("llm", llm_node)     # the brain
    graph.add_node("tools", tool_node)  # the tool executor

    # the graph always starts at the llm node
    graph.set_entry_point("llm")

    # after llm runs, check if it called a tool or not
    graph.add_conditional_edges(
        "llm",            # from this node
        should_continue,  # call this function to decide
        {
            "tools": "tools",  # if it returned "tools" → go to tool_node
            END: END           # if it returned END → stop
        }
    )

    # after tools run, always go back to llm so it can process the result
    graph.add_edge("tools", "llm")

    # compile and return the runnable graph
    return graph.compile()
