"""
sub_agents.py — AgriShield AI: Specialized Agronomic Sub-Agents & Risk Critic
-----------------------------------------------------------------------------
Defines 3 domain specialist agents and 1 Evaluator-Critic reflection agent:

1. 💧 IrrigationSentinelAgent    → Soil moisture balance, ET₀, pump scheduling
2. 🐛 PestDiseaseForecasterAgent → Fungal spore germination, humidity risks, bio/chemical control
3. 🚜 HarvestSprayAdvisorAgent   → Wind drift risk (<15 km/h), rain wash-off, dry harvest windows
4. 🛡️ SafetyRiskCriticAgent      → Evaluator/Reflection node that audits recommendations,
                                   verifies threshold constraints, and assigns Crop Threat Index.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

# Shared high-speed LLM on Groq (fallback placeholder ensures clean import on cloud platforms)
_llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY") or "gsk_placeholder",
    temperature=0.25
)

# Friendly UI display labels
SUB_AGENT_LABELS = {
    "irrigation_sentinel":    "💧 Irrigation Sentinel",
    "pest_disease_forecaster":"🐛 Pest & Disease Forecaster",
    "harvest_spray_advisor":  "🚜 Harvest & Spray Advisor",
    "safety_risk_critic":     "🛡️ Safety & Risk Critic",
    "off_topic":              "🚫 General Guardrail",
}


# =====================================================================
# Sub-Agent 1: 💧 Irrigation & Water Sentinel
# =====================================================================
IRRIGATION_AGENT_PROMPT = """\
You are the Irrigation & Water Sentinel for AgriShield AI.
Your role: Optimize groundwater usage, compute soil water balance, and give precise pump running advice.

Input: User question, Farm Profile, and live Agro-Meteorological Telemetry (ET₀, soil moisture, rainfall).

Guidelines:
1. Clear Operational Decision: Begin with a bold verdict:
   - **PAUSE PUMPS / DO NOT IRRIGATE** (if rain is predicted or soil moisture > 0.30 m³/m³)
   - **IRRIGATE TODAY** (if soil is in deficit < 0.18 m³/m³ and no rain in 48h)
   - **LIGHT DEFICIT IRRIGATION** (if ET₀ is high but soil has moderate reserve)
2. Quantitative Justification: Mention Reference Evapotranspiration (ET₀ mm/day) and Expected Rainfall (mm).
3. Water Savings Estimate: State estimated water/electricity saved if irrigation is skipped.
4. Timing: If irrigation is needed, suggest drip/early morning/late evening hours to minimize evaporative loss.
Keep response direct, authoritative, and under 5 sentences.
"""

def irrigation_sentinel(user_query: str, farm_context: str, weather_data: str) -> str:
    messages = [
        SystemMessage(content=IRRIGATION_AGENT_PROMPT),
        HumanMessage(content=f"Farm Profile:\n{farm_context}\n\nUser Question:\n{user_query}\n\nAgro-Meteorological Telemetry:\n{weather_data}")
    ]
    response = _llm.invoke(messages)
    return response.content


# =====================================================================
# Sub-Agent 2: 🐛 Pest & Fungal Disease Forecaster
# =====================================================================
PEST_AGENT_PROMPT = """\
You are the Pest & Disease Forecaster for AgriShield AI.
Your role: Forecast fungal blights, rusts, mildew, and insect infestations based on atmospheric humidity, temperature, and leaf wetness.

Input: User question, Farm Profile (Crop & Stage), and live Agro-Meteorological Telemetry (RH%, temp, rain).

Guidelines:
1. Threat Level Verdict: State if the current weather creates **HIGH**, **MODERATE**, or **LOW** disease incubation pressure.
2. Biology & Mechanism: Connect the parameters:
   - High humidity (>80%) + warm temp (22-30°C) triggers fungal spore germination (e.g. Downy Mildew, Early Blight).
   - Overcast cloudy days trigger sucking pests (Aphids, Jassids, Whiteflies).
3. Preventative Action:
   - Emphasize spraying BEFORE rain/high-moisture events (preventative systemic or contact fungicide/neem oil).
   - Do NOT spray if immediate rain will wash away chemicals.
4. Safe Harvesting Interval (PHI): Remind farmer about safety waiting periods if crop is near maturity.
Keep response crisp, actionable, and under 5 sentences.
"""

def pest_disease_forecaster(user_query: str, farm_context: str, weather_data: str) -> str:
    messages = [
        SystemMessage(content=PEST_AGENT_PROMPT),
        HumanMessage(content=f"Farm Profile:\n{farm_context}\n\nUser Question:\n{user_query}\n\nAgro-Meteorological Telemetry:\n{weather_data}")
    ]
    response = _llm.invoke(messages)
    return response.content


# =====================================================================
# Sub-Agent 3: 🚜 Harvest & Chemical Spray Advisor
# =====================================================================
HARVEST_SPRAY_PROMPT = """\
You are the Harvest & Spray Chemical Advisor for AgriShield AI.
Your role: Optimize field chemical applications and safe crop harvesting windows.

Input: User question, Farm Profile, and live Agro-Meteorological Telemetry (Wind speed, rain probability, 3-day sky conditions).

Guidelines:
1. Spraying Physics & Drift Rules:
   - Ideal wind speed: 5 to 15 km/h.
   - Wind > 15 km/h: **SPRAY DRIFT HAZARD** — chemical misses target, wastes money, and risks neighboring crops.
   - Rain within 4-6 hours: **WASH-OFF HAZARD** — chemical washes away before rain-fast absorption.
2. Harvesting Window Rules:
   - Harvesting grains/cotton requires a minimum of **3 consecutive dry days** with low relative humidity.
   - Wet harvesting leads to fungal grain rot, aflatoxins, and downgraded market prices.
3. Operational Recommendation:
   - Give a clear **GO / HOLD / RESCHEDULE** decision with optimal time windows (e.g., 07:00 AM - 10:30 AM).
Keep response highly practical and under 5 sentences.
"""

def harvest_spray_advisor(user_query: str, farm_context: str, weather_data: str) -> str:
    messages = [
        SystemMessage(content=HARVEST_SPRAY_PROMPT),
        HumanMessage(content=f"Farm Profile:\n{farm_context}\n\nUser Question:\n{user_query}\n\nAgro-Meteorological Telemetry:\n{weather_data}")
    ]
    response = _llm.invoke(messages)
    return response.content


# =====================================================================
# Sub-Agent 4: 🛡️ Safety & Crop Risk Critic (Evaluator / Reflection Node)
# =====================================================================
CRITIC_AGENT_PROMPT = """\
You are the Safety & Crop Risk Critic for AgriShield AI.
You perform the LangGraph Reflection / Self-Correction evaluation step.

Your task:
Review the draft advice generated by the specialist sub-agent against raw environmental telemetry.
Ensure:
1. No dangerous advice (e.g., advising spraying during 25+ km/h wind or heavy downpour).
2. Correct threat score assigned.
3. Added safety guardrail (e.g. pollinator safety, protective gear, runoff warning).

Output Format:
Return the final finalized response in this exact structured markdown format:

{SPECIALIST_ADVICE}

---
🛡️ **AgriShield Audit & Risk Assessment:**
• **Crop Threat Index:** [LOW 🟢 | MODERATE 🟡 | SEVERE 🔴]
• **Key Environmental Threshold:** (e.g., Wind 18 km/h > 15 km/h limit OR Humidity 84% > 80% threshold)
• **Safety & Environmental Guardrail:** (1 sentence on pollinator/worker safety or drainage)
"""

def safety_risk_critic(draft_advice: str, weather_data: str, crop_name: str) -> str:
    messages = [
        SystemMessage(content=CRITIC_AGENT_PROMPT),
        HumanMessage(content=f"Target Crop: {crop_name}\n\nRaw Telemetry:\n{weather_data}\n\nDraft Specialist Advice:\n{draft_advice}")
    ]
    response = _llm.invoke(messages)
    return response.content


# Sub-agents mapping dictionary
SUB_AGENTS = {
    "irrigation_sentinel":    irrigation_sentinel,
    "pest_disease_forecaster":pest_disease_forecaster,
    "harvest_spray_advisor":  harvest_spray_advisor,
}
