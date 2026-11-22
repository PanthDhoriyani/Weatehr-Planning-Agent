"""
nodes.py — AgriShield AI: Supervisor, LLM Brain, Dispatcher & Reflection Critic
-------------------------------------------------------------------------------
Nodes in the LangGraph graph:
1. supervisor_node         → Classifies farmer intent into domain sub-agent
2. llm_node                → Injects Farm Profile memory & binds agricultural tools
3. tool_node               → Executes Open-Meteo Agricultural API tool
4. sub_agent_dispatch_node → Invokes specialized agronomic sub-agent
5. critic_node             → Reflection/Evaluator node auditing advice & assigning threat index
"""

import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage, ToolMessage
from langgraph.prebuilt import ToolNode

from .tools import get_agricultural_weather_data
from .state import AgentState
from .memory import get_memory_context, get_farm_profile, remember_agri_advisory
from .sub_agents import SUB_AGENTS, safety_risk_critic

load_dotenv()

# =====================================================================
# AGRI-SHIELD BASE SYSTEM PROMPT
# =====================================================================
BASE_SYSTEM_PROMPT = """\
You are AgriShield AI — an Autonomous Climate & Precision Agriculture Sentinel.
Your mission is to help farmers make data-driven agronomic decisions regarding:
- Precision Irrigation & Soil Water Balance (Evapotranspiration ET₀, soil moisture)
- Fungal Disease & Pest Outbreak Prevention (Humidity, temperature, leaf wetness)
- Field Operations, Chemical Spraying Windows & Harvest Timing (Wind drift, rain wash-off)

Topics to REJECT:
- Questions completely unrelated to agriculture, farming, crops, soil, water, pesticides, or rural meteorology
  (e.g., coding, movies, politics, algebra).

When you REJECT an off-topic question, say:
"🌱 AgriShield AI is dedicated exclusively to precision agriculture and farm advisory. Please ask an agronomic or crop-weather question!"

When you answer an agronomic question:
1. Always invoke the `get_agricultural_weather_data` tool with the farm location and target crop.
2. If the user does not specify a location, use their active Farm Profile location.
3. If the user does not specify a crop, use their active Farm Profile crop.
"""

# =====================================================================
# SUPERVISOR SYSTEM PROMPT
# =====================================================================
SUPERVISOR_PROMPT = """\
You are the AgriShield Supervisor Agent.
Classify the incoming farmer query and route it to the exact specialist sub-agent.

Sub-Agents:
1. irrigation_sentinel
   - Keywords: water, irrigate, pump, soil moisture, drought, evapotranspiration, dry soil, drip, borewell, electricity.
2. pest_disease_forecaster
   - Keywords: pests, insects, fungus, blight, rust, mildew, whitefly, aphids, worms, rot, disease, spores, infection.
3. harvest_spray_advisor
   - Keywords: spray, pesticide, fungicide, herbicide, fertilizer, wind drift, rain wash, harvest, cutting, threshing, storage.

If the question is unrelated to agriculture, farming, crops, irrigation, pests, field spraying, harvest, soil, or rural weather (e.g. coding, math, trivia, movies, sports, history, politics, jokes), you MUST reply with:
   off_topic

Respond with ONLY ONE token from:
irrigation_sentinel
pest_disease_forecaster
harvest_spray_advisor
off_topic
"""

# Shared LLM (fallback placeholder ensures clean import on cloud platforms)
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY") or "gsk_placeholder",
    temperature=0.25
)

tools_list = [get_agricultural_weather_data]
llm_with_tools = llm.bind_tools(tools_list)
tool_node = ToolNode(tools_list)


# =====================================================================
# NODE 1: SUPERVISOR NODE
# =====================================================================
def supervisor_node(state: AgentState) -> dict:
    """Classifies user intent and routes to the appropriate specialist agent."""
    messages = state["messages"]
    user_msg = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_msg = msg.content
            break

    profile = get_farm_profile()

    response = llm.invoke([
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=f"Active Farm Profile: Location={profile.get('location')}, Crop={profile.get('crop')}\n\nFarmer Query: {user_msg}")
    ])

    routing = response.content.strip().lower()
    valid_routes = {"irrigation_sentinel", "pest_disease_forecaster", "harvest_spray_advisor", "off_topic"}

    if routing not in valid_routes:
        # Default fallback heuristic
        q_lower = user_msg.lower()
        if any(w in q_lower for w in ["water", "pump", "irrigate", "dry"]):
            routing = "irrigation_sentinel"
        elif any(w in q_lower for w in ["pest", "disease", "blight", "fungus", "worm"]):
            routing = "pest_disease_forecaster"
        elif any(w in q_lower for w in ["spray", "harvest", "cut", "wind"]):
            routing = "harvest_spray_advisor"
        else:
            routing = "off_topic"

    return {
        "active_agent": routing,
        "crop_name": profile.get("crop", "Cotton"),
        "growth_stage": profile.get("growth_stage", "Flowering"),
        "farm_location": profile.get("location", "Pune")
    }


# =====================================================================
# NODE 2: LLM NODE (Brain + Tool Caller)
# =====================================================================
def llm_node(state: AgentState) -> dict:
    """Reasoning node that reads Farm Profile memory and calls the agricultural tool."""
    active_agent = state.get("active_agent", "irrigation_sentinel")

    # Fast guardrail rejection for off-topic queries
    if active_agent == "off_topic":
        refusal = AIMessage(
            content="🌱 AgriShield AI is dedicated exclusively to precision agriculture and farm advisory. Please ask an agronomic or crop-weather question!"
        )
        return {"messages": [refusal]}

    memory_ctx = get_memory_context()
    full_prompt = f"{BASE_SYSTEM_PROMPT}\n\n── Farm Profile & Long-Term Memory ──\n{memory_ctx}\n────────────────────────────────────────"

    full_messages = [SystemMessage(content=full_prompt)] + list(state["messages"])
    response = llm_with_tools.invoke(full_messages)
    return {"messages": [response]}


# =====================================================================
# NODE 3: SUB-AGENT DISPATCH NODE
# =====================================================================
def sub_agent_dispatch_node(state: AgentState) -> dict:
    """Dispatches fetched agricultural telemetry to the designated specialist sub-agent."""
    active_agent = state.get("active_agent", "irrigation_sentinel")
    crop_name = state.get("crop_name", "Cotton")
    growth_stage = state.get("growth_stage", "Flowering")
    location = state.get("farm_location", "Pune")

    user_query = ""
    weather_data = ""

    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            user_query = msg.content
        if isinstance(msg, ToolMessage):
            weather_data = msg.content

    if not weather_data:
        weather_data = f"Weather telemetry unavailable for {location}."

    farm_context = f"Location: {location} | Crop: {crop_name} | Stage: {growth_stage}"

    # Call the routed specialist
    agent_fn = SUB_AGENTS.get(active_agent, SUB_AGENTS["irrigation_sentinel"])
    draft_advice = agent_fn(user_query, farm_context, weather_data)

    return {
        "weather_data": weather_data,
        "critic_notes": draft_advice
    }


# =====================================================================
# NODE 4: CRITIC & REFLECTION NODE (Evaluator-Optimizer)
# =====================================================================
def critic_node(state: AgentState) -> dict:
    """
    Evaluator-Optimizer Reflection Step:
    Audits the specialist's draft advice against environmental thresholds,
    assigns the Crop Threat Index, and persists the advisory to Long-Term Memory.
    """
    draft_advice = state.get("critic_notes", "")
    weather_data = state.get("weather_data", "")
    crop_name = state.get("crop_name", "Cotton")
    location = state.get("farm_location", "Pune")
    active_agent = state.get("active_agent", "irrigation_sentinel")

    # User query extraction
    user_query = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            user_query = msg.content
            break

    # Perform reflection evaluation
    final_response = safety_risk_critic(draft_advice, weather_data, crop_name)

    # Determine threat level from response
    threat_level = "MODERATE"
    if "SEVERE" in final_response:
        threat_level = "SEVERE"
    elif "LOW" in final_response:
        threat_level = "LOW"

    # Persist advisory to Long-Term Memory
    remember_agri_advisory(
        location=location,
        crop=crop_name,
        agent_name=active_agent,
        query=user_query,
        advice_summary=draft_advice[:200],
        threat_level=threat_level
    )

    return {
        "messages": [AIMessage(content=final_response)],
        "threat_level": threat_level
    }
