from typing import TypedDict, Annotated, Optional
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """
    AgriShield AI AgentState.
    Tracks conversation messages, active specialist sub-agent,
    farm & crop profile context, environmental sensor data, and risk critique.
    """
    # LangGraph message history (short-term memory via operator.add)
    messages: Annotated[list[BaseMessage], operator.add]

    # Injected long-term memory (Farm Profile & Advisory History from memory.json)
    memory_context: Optional[str]

    # Active specialist sub-agent routed by Supervisor:
    # "irrigation_sentinel" | "pest_disease_forecaster" | "harvest_spray_advisor" | "off_topic"
    active_agent: Optional[str]

    # Farm and crop contextual attributes
    crop_name: Optional[str]
    growth_stage: Optional[str]
    farm_location: Optional[str]

    # Raw agricultural & meteorological telemetry from Open-Meteo
    weather_data: Optional[str]

    # Reflection / Critic audit score and safety notes
    threat_level: Optional[str]  # e.g., "LOW", "MODERATE", "SEVERE"
    critic_notes: Optional[str]
