from typing import TypedDict, Annotated, Optional
from langchain_core.messages import BaseMessage
import operator

# AgentState is basically the "memory" of our agent
# every node in the graph reads from this and writes back to this
# the 'messages' list keeps growing as the agent takes more steps

class AgentState(TypedDict):
    # operator.add means new messages get ADDED to the list (not replaced)
    messages: Annotated[list[BaseMessage], operator.add]

    # ── Unit 3 Extension: Memory ──────────────────────────────────────────
    # Injected long-term memory summary (from memory.json) so the LLM
    # can reference what the user has asked about before.
    memory_context: Optional[str]

    # ── Unit 4 Extension: Multi-Agent ────────────────────────────────────
    # Tracks which specialized sub-agent handled the current query.
    # Used by the Streamlit UI to show the active agent badge.
    active_agent: Optional[str]   # e.g. "weather_agent" | "outfit_advisor" | "travel_planner"

    # Stores the raw weather data fetched during this turn
    # so sub-agents can access it without calling the tool again.
    weather_data: Optional[str]
