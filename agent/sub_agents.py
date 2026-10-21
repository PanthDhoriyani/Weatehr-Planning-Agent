"""
sub_agents.py — Unit 4 Extension: Multi-Agent System
------------------------------------------------------
Defines 3 specialized sub-agents that the Supervisor can delegate to.

Each sub-agent is a function that:
  1. Receives the user's query + weather data (if fetched)
  2. Has its own focused system prompt / persona
  3. Returns a structured response dict

Sub-Agents:
  1. WeatherAgent       → Plain weather forecasts & rain queries
  2. OutfitAdvisorAgent → Clothing recommendations based on weather
  3. TravelPlannerAgent → Travel suitability based on weather
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

# ---------------------------------------------------------------
# Shared LLM for all sub-agents (same model, different prompts)
# ---------------------------------------------------------------
_llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3
)


# ---------------------------------------------------------------
# Sub-Agent 1: Weather Agent
# ---------------------------------------------------------------
WEATHER_AGENT_PROMPT = """\
You are a precise Weather Forecaster sub-agent.
Your ONLY job: interpret raw weather data and give a clear, concise forecast answer.
Rules:
- Always state rain probability and temperature.
- Give a direct YES/NO recommendation (umbrella / raincoat / stay indoors).
- Keep your answer under 4 sentences.
- Do NOT advise on clothing, travel, or anything else — just the weather.
"""

def weather_agent(user_query: str, weather_data: str) -> str:
    """
    Specialized sub-agent for pure weather forecast queries.
    """
    messages = [
        SystemMessage(content=WEATHER_AGENT_PROMPT),
        HumanMessage(content=f"User question: {user_query}\n\nWeather data:\n{weather_data}")
    ]
    response = _llm.invoke(messages)
    return response.content


# ---------------------------------------------------------------
# Sub-Agent 2: Outfit Advisor Agent
# ---------------------------------------------------------------
OUTFIT_AGENT_PROMPT = """\
You are a friendly Outfit Advisor sub-agent.
Your ONLY job: recommend what to wear based on weather conditions.
Rules:
- Suggest 2-3 specific clothing items (e.g., "wear a light jacket and carry a compact umbrella").
- Tailor advice for the temperature range (hot vs cold vs rainy).
- Keep your answer practical and friendly.
- Under 5 sentences.
"""

def outfit_advisor_agent(user_query: str, weather_data: str) -> str:
    """
    Specialized sub-agent for clothing/outfit recommendations based on weather.
    """
    messages = [
        SystemMessage(content=OUTFIT_AGENT_PROMPT),
        HumanMessage(content=f"User question: {user_query}\n\nWeather data:\n{weather_data}")
    ]
    response = _llm.invoke(messages)
    return response.content


# ---------------------------------------------------------------
# Sub-Agent 3: Travel Planner Agent
# ---------------------------------------------------------------
TRAVEL_AGENT_PROMPT = """\
You are an intelligent Travel Planner sub-agent.
Your ONLY job: assess whether the weather is suitable for travel or outdoor activities.
Rules:
- Give a clear GO / DELAY / AVOID recommendation.
- Mention key weather risks for travel (heavy rain, storms, extreme heat/cold).
- Suggest the best time window if travel is possible.
- Keep your answer under 5 sentences.
"""

def travel_planner_agent(user_query: str, weather_data: str) -> str:
    """
    Specialized sub-agent for travel suitability assessment based on weather.
    """
    messages = [
        SystemMessage(content=TRAVEL_AGENT_PROMPT),
        HumanMessage(content=f"User question: {user_query}\n\nWeather data:\n{weather_data}")
    ]
    response = _llm.invoke(messages)
    return response.content


# ---------------------------------------------------------------
# Sub-Agent Registry — used by the supervisor
# ---------------------------------------------------------------
SUB_AGENTS = {
    "weather_agent":       weather_agent,
    "outfit_advisor":      outfit_advisor_agent,
    "travel_planner":      travel_planner_agent,
}

# Human-readable labels for UI display
SUB_AGENT_LABELS = {
    "weather_agent":   "🌦️ Weather Agent",
    "outfit_advisor":  "👗 Outfit Advisor",
    "travel_planner":  "✈️ Travel Planner",
}
