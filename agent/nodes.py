"""
nodes.py — LLM nodes, Supervisor, and Tool Node
-------------------------------------------------
Original:  llm_node + tool_node
Added:
  - Memory injection into system prompt       (Unit 3)
  - supervisor_node to route between agents   (Unit 4)
  - sub-agent invocation after tool call      (Unit 4)
"""

import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.prebuilt import ToolNode

from .tools import get_weather_forecast
from .state import AgentState
from .memory import get_memory_context, remember_city
from .sub_agents import SUB_AGENTS, SUB_AGENT_LABELS

load_dotenv()

# ---------------------------------------------------------------
# BASE SYSTEM PROMPT — weather guardrails (unchanged from original)
# ---------------------------------------------------------------
BASE_SYSTEM_PROMPT = """\
You are a helpful Weather Assistant. Your ONLY job is to answer questions related to weather.

Topics you CAN answer:
- Rain, drizzle, showers, thunderstorms, snowfall
- Whether to carry an umbrella, raincoat, jacket, or similar
- Temperature, humidity, wind, fog, clouds
- Weather forecasts for any city
- General advice based on weather (like "should I go out?", "what to wear?")

Topics you MUST REJECT (politely):
- Anything not related to weather at all
- Examples of stuff to reject: maths problems, coding help, movie suggestions,
  history questions, sports scores, cooking tips, etc.

When you REJECT a question, say exactly:
"Sorry, I can only answer weather-related questions! 🌤️ Please ask me something about the weather."

When you ANSWER a weather question:
1. Use the get_weather_forecast tool to get real weather data
2. Give a clear YES or NO recommendation (e.g., "Yes, carry an umbrella!" or "No, skies are clear!")
3. Explain why, based on the data
4. Keep it friendly and short
"""

# ---------------------------------------------------------------
# SUPERVISOR SYSTEM PROMPT — Unit 4: Multi-Agent routing
# ---------------------------------------------------------------
SUPERVISOR_PROMPT = """\
You are a Supervisor Agent that classifies incoming weather-related questions
and routes them to the correct specialist sub-agent.

Available sub-agents:
  1. weather_agent   → Plain weather forecast / rain queries
     Examples: "Will it rain?", "What is the weather tomorrow?", "Umbrella needed?"
  2. outfit_advisor  → Clothing and outfit recommendations
     Examples: "What should I wear?", "What clothes for tomorrow?", "Dress code for rain?"
  3. travel_planner  → Travel suitability and outdoor activity planning
     Examples: "Good day to travel?", "Can I go to Goa?", "Is it safe to drive to Lonavala?"

IMPORTANT: You must respond with ONLY ONE of these exact strings (no extra text):
  weather_agent
  outfit_advisor
  travel_planner

If the question is off-topic (not weather-related), respond with:
  off_topic
"""

# ---------------------------------------------------------------
# LLM Setup (shared model)
# ---------------------------------------------------------------
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3
)

tools_list = [get_weather_forecast]
llm_with_tools = llm.bind_tools(tools_list)

# ToolNode handles actually running whichever tool the LLM picked
tool_node = ToolNode(tools_list)


# ---------------------------------------------------------------
# SUPERVISOR NODE — Unit 4: decides which sub-agent handles query
# ---------------------------------------------------------------
def supervisor_node(state: AgentState) -> dict:
    """
    Reads the latest user message and decides which sub-agent to route to.
    Sets state['active_agent'] accordingly.
    """
    user_msg = state["messages"][-1].content

    response = llm.invoke([
        SystemMessage(content=SUPERVISOR_PROMPT),
        {"role": "user", "content": user_msg}
    ])

    routing = response.content.strip().lower()

    # safety: default to weather_agent if unexpected output
    valid_routes = {"weather_agent", "outfit_advisor", "travel_planner", "off_topic"}
    if routing not in valid_routes:
        routing = "weather_agent"

    return {"active_agent": routing}


# ---------------------------------------------------------------
# LLM NODE — brain node (reads memory context + system prompt)
# Unit 3: memory context is injected here
# ---------------------------------------------------------------
def llm_node(state: AgentState) -> dict:
    """
    The main reasoning node. Injects long-term memory into system prompt
    so the LLM is aware of past queries.
    """
    messages = state["messages"]
    active_agent = state.get("active_agent", "weather_agent")

    # ── Unit 3: Long-Term Memory injection ───────────────────────
    memory_ctx = get_memory_context()
    memory_section = f"""
── Long-Term Memory (User History) ──
{memory_ctx}
──────────────────────────────────────
"""

    # Off-topic handling — don't even call the tool
    if active_agent == "off_topic":
        refusal = AIMessage(
            content="Sorry, I can only answer weather-related questions! 🌤️ Please ask me something about the weather."
        )
        return {"messages": [refusal]}

    full_prompt = BASE_SYSTEM_PROMPT + memory_section

    full_messages = [SystemMessage(content=full_prompt)] + messages
    response = llm_with_tools.invoke(full_messages)
    return {"messages": [response]}


# ---------------------------------------------------------------
# SUB-AGENT DISPATCH NODE — Unit 4
# Called AFTER tool_node has fetched weather data.
# Routes to the correct sub-agent for a specialized response.
# ---------------------------------------------------------------
def sub_agent_dispatch_node(state: AgentState) -> dict:
    """
    After weather data has been fetched by the tool node, this node:
    1. Extracts the weather data from the last ToolMessage
    2. Calls the appropriate sub-agent
    3. Returns the sub-agent's answer as an AIMessage
    Also saves the city + recommendation to long-term memory (Unit 3).
    """
    from langchain_core.messages import ToolMessage

    active_agent = state.get("active_agent", "weather_agent")
    user_query   = ""
    weather_data = ""

    # find user query and weather tool result from messages
    for msg in state["messages"]:
        from langchain_core.messages import HumanMessage
        if isinstance(msg, HumanMessage):
            user_query = msg.content
        if isinstance(msg, ToolMessage):
            weather_data = msg.content

    # if no weather data found (shouldn't happen, but safety check)
    if not weather_data:
        weather_data = "No weather data available."

    # Call the appropriate sub-agent
    agent_fn = SUB_AGENTS.get(active_agent, SUB_AGENTS["weather_agent"])
    answer   = agent_fn(user_query, weather_data)

    # ── Unit 3: Save to Long-Term Memory ─────────────────────────
    # Extract city name from weather_data (first line usually has it)
    city_match = re.search(r"forecast for (.+?):", weather_data)
    if city_match:
        city = city_match.group(1).strip()
        remember_city(city, answer[:200])

    return {
        "messages": [AIMessage(content=answer)],
        "weather_data": weather_data,
    }
