import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from .tools import get_weather_forecast
from .state import AgentState

load_dotenv()

# ---------------------------------------------------------------
# SYSTEM PROMPT — this tells the LLM what its job is
# and what questions to reject (off-topic stuff)
# ---------------------------------------------------------------
SYSTEM_PROMPT = """
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

How to handle tricky weather questions:
- "Will it be wet tomorrow?" → YES, answer this (it's about rain)
- "Do I need to carry something extra?" → Check context; if weather-related, answer it
- "Is it going to pour?" → YES, answer this
- "Should I take my bike?" → If asking because of weather, answer it
- "What's the vibe outside tomorrow?" → Answer it as a weather question
- "Capital of France?" → REJECT, say you only handle weather questions
- "Solve 2+2" → REJECT
- "Which team won IPL?" → REJECT

When you REJECT a question, say exactly:
"Sorry, I can only answer weather-related questions! 🌤️ Please ask me something about the weather."

When you ANSWER a weather question:
1. Use the get_weather_forecast tool to get real weather data
2. Give a clear YES or NO recommendation (e.g., "Yes, carry an umbrella!" or "No, skies are clear!")
3. Explain why, based on the data
4. Keep it friendly and short
"""

# ---------------------------------------------------------------
# setup Groq LLM (free tier, super fast)
# ---------------------------------------------------------------
llm = ChatGroq(
    model="openai/gpt-oss-120b",   # confirmed: supports tool calling on this account
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3   # a little low so it doesn't make stuff up
)

# list of tools the LLM is allowed to use
tools_list = [get_weather_forecast]

# bind tools to LLM so it knows it can call them
llm_with_tools = llm.bind_tools(tools_list)

# ToolNode handles actually running whichever tool the LLM picked
tool_node = ToolNode(tools_list)


# ---------------------------------------------------------------
# LLM Node — the "brain" node
# this is where the LLM reads messages and decides what to do
# ---------------------------------------------------------------
def llm_node(state: AgentState):
    messages = state["messages"]

    # always prepend the system prompt so LLM knows its rules
    full_messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    # call the LLM
    response = llm_with_tools.invoke(full_messages)

    # return the response; LangGraph will add it to state["messages"]
    return {"messages": [response]}
