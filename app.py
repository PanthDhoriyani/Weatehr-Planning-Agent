"""
app.py — AgriShield AI: Autonomous Climate & Precision Agriculture Sentinel
----------------------------------------------------------------------------
Interactive Streamlit UI featuring:
- Interactive Farm Profile (Location, Crop, Growth Stage, Soil Type)
- Live Multi-Agent Status (Irrigation, Pest/Disease, Harvest/Spray, Reflection Critic)
- Agro-Meteorological Telemetry Inspector
- Persistent Long-Term Farm Memory Panel
"""

import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Bridge Streamlit Cloud Secrets to os.environ
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from agent.graph import build_graph
from agent.memory import (
    get_farm_profile,
    update_farm_profile,
    get_all_memory,
    clear_memory
)
from agent.sub_agents import SUB_AGENT_LABELS

# ---------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------
st.set_page_config(
    page_title="AgriShield AI — Precision Agriculture Sentinel",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------
# Custom Styling
# ---------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0d1b12, #132a1c, #0b1a24);
        color: #e2e8f0;
    }

    [data-testid="stSidebar"] {
        background: rgba(15, 30, 20, 0.75);
        border-right: 1px solid rgba(74, 222, 128, 0.15);
        backdrop-filter: blur(12px);
    }

    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #4ade80, #38bdf8, #a3e635);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    .user-bubble {
        background: linear-gradient(135deg, #1e3a8a, #0369a1);
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0 8px 60px;
        font-size: 0.95rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }

    .agent-bubble {
        background: rgba(22, 45, 30, 0.65);
        border: 1px solid rgba(74, 222, 128, 0.25);
        color: #f1f5f9;
        padding: 14px 20px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 60px 8px 0;
        font-size: 0.95rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 14px rgba(0,0,0,0.3);
    }

    .telemetry-box {
        background: rgba(14, 165, 233, 0.08);
        border-left: 3px solid #38bdf8;
        padding: 10px 14px;
        border-radius: 0 8px 8px 0;
        margin: 8px 0;
        font-size: 0.82rem;
        color: #bae6fd;
        font-family: monospace;
        white-space: pre-wrap;
    }

    .tool-box {
        background: rgba(234, 179, 8, 0.1);
        border-left: 3px solid #eab308;
        padding: 8px 14px;
        border-radius: 0 8px 8px 0;
        margin: 6px 0;
        font-size: 0.82rem;
        color: #fef08a;
        font-family: monospace;
    }

    .agent-badge {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.3px;
        margin-bottom: 6px;
    }
    .badge-irrigation { background: rgba(56, 189, 248, 0.2); border: 1px solid #38bdf8; color: #38bdf8; }
    .badge-pest       { background: rgba(239, 68, 68, 0.2); border: 1px solid #f87171; color: #f87171; }
    .badge-harvest    { background: rgba(251, 191, 36, 0.2); border: 1px solid #fbbf24; color: #fbbf24; }
    .badge-critic     { background: rgba(168, 85, 247, 0.2); border: 1px solid #c084fc; color: #c084fc; }
    .badge-off_topic  { background: rgba(148, 163, 184, 0.2); border: 1px solid #94a3b8; color: #94a3b8; }

    .threat-tag {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.70rem;
        font-weight: 700;
        margin-left: 8px;
    }
    .threat-low      { background: rgba(74, 222, 128, 0.25); color: #4ade80; border: 1px solid #4ade80; }
    .threat-moderate { background: rgba(250, 204, 21, 0.25); color: #facc15; border: 1px solid #facc15; }
    .threat-severe   { background: rgba(248, 113, 113, 0.25); color: #f87171; border: 1px solid #f87171; }

    .memory-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 10px 12px;
        margin: 6px 0;
        font-size: 0.80rem;
        color: #cbd5e1;
    }

    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.08) !important;
        color: white !important;
        border: 1px solid rgba(74, 222, 128, 0.3) !important;
        border-radius: 10px !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #15803d, #047857);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1.8rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #16a34a, #059669);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------
# Badge Helpers
# ---------------------------------------------------------------
def agent_badge_html(agent_key: str, threat: str = None) -> str:
    label = SUB_AGENT_LABELS.get(agent_key, "🤖 AgriShield Agent")
    cls_map = {
        "irrigation_sentinel":     "badge-irrigation",
        "pest_disease_forecaster": "badge-pest",
        "harvest_spray_advisor":   "badge-harvest",
        "safety_risk_critic":      "badge-critic",
        "off_topic":               "badge-off_topic",
    }
    cls = cls_map.get(agent_key, "badge-irrigation")

    html = f'<span class="agent-badge {cls}">{label}</span>'
    if threat:
        t_cls = "threat-moderate"
        if "SEVERE" in threat:
            t_cls = "threat-severe"
        elif "LOW" in threat:
            t_cls = "threat-low"
        html += f'<span class="threat-tag {t_cls}">THREAT: {threat}</span>'

    return html


# ---------------------------------------------------------------
# State Initialization
# ---------------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "agent_app" not in st.session_state:
    with st.spinner("Initializing AgriShield Multi-Agent Graph..."):
        st.session_state.agent_app = build_graph()


# ---------------------------------------------------------------
# SIDEBAR: Farm Profile + Memory + Multi-Agent Roster
# ---------------------------------------------------------------
with st.sidebar:
    # Free deployment API key fallback (if not set in st.secrets or .env)
    current_key = os.getenv("GROQ_API_KEY", "")
    if not current_key or current_key == "gsk_placeholder":
        st.warning("⚠️ **Groq API Key Required**")
        api_key_input = st.text_input("Enter Groq API Key:", type="password", placeholder="gsk_...", key="groq_key_input")
        if api_key_input:
            os.environ["GROQ_API_KEY"] = api_key_input.strip()
            from agent.nodes import llm
            from agent.sub_agents import _llm
            llm.api_key = api_key_input.strip()
            _llm.api_key = api_key_input.strip()
            st.session_state.agent_app = build_graph()
            st.success("✅ API Key connected!")
            st.rerun()
        st.caption("Get a free key in 30 seconds at [console.groq.com](https://console.groq.com)")
        st.markdown("---")

    st.markdown("### 🌾 Active Farm Profile")
    st.caption("Unit 3 Extension — Persistent Farm Context")

    curr_profile = get_farm_profile()

    with st.form("farm_profile_form"):
        loc_input = st.text_input("Farm Location / District", value=curr_profile.get("location", "Pune"))

        crop_options = ["Cotton", "Wheat", "Tomato", "Sugarcane", "Rice / Paddy", "Soybean", "Onion", "Chilli", "Maize"]
        current_crop = curr_profile.get("crop", "Cotton")
        crop_idx = crop_options.index(current_crop) if current_crop in crop_options else 0
        crop_input = st.selectbox("Target Crop", crop_options, index=crop_idx)

        stage_options = [
            "Sowing & Germination",
            "Vegetative Canopy",
            "Flowering / Boll Formation",
            "Fruit / Pod Maturation",
            "Ready for Harvesting"
        ]
        current_stage = curr_profile.get("growth_stage", "Flowering / Boll Formation")
        stage_idx = stage_options.index(current_stage) if current_stage in stage_options else 2
        stage_input = st.selectbox("Growth Stage", stage_options, index=stage_idx)

        soil_options = ["Black Cotton Soil (Vertisol)", "Alluvial Loam", "Sandy Loam", "Red Soil (Alfisol)"]
        curr_soil = curr_profile.get("soil_type", "Black Cotton Soil (Vertisol)")
        soil_idx = soil_options.index(curr_soil) if curr_soil in soil_options else 0
        soil_input = st.selectbox("Soil Type", soil_options, index=soil_idx)

        save_profile_btn = st.form_submit_button("💾 Save Profile")
        if save_profile_btn:
            update_farm_profile(loc_input, crop_input, stage_input, soil_input)
            st.success("Farm profile updated!")
            st.rerun()

    st.markdown("---")

    # ── Multi-Agent Architecture ──────────────────────────────────
    st.markdown("### 🤖 Multi-Agent Roster")
    st.caption("Unit 4 + Reflection Critic")
    st.markdown("""
- 💧 **Irrigation Sentinel** (ET₀ & Soil Moisture)
- 🐛 **Pest/Disease Forecaster** (Fungal/Humidity)
- 🚜 **Harvest & Spray Advisor** (Wind Drift & Wash-off)
- 🛡️ **Safety & Risk Critic** (Evaluator-Optimizer)
""")

    st.markdown("---")

    # ── Unit 3: Long-Term Memory Panel ────────────────────────────
    st.markdown("### 📚 Farm Advisory Memory")
    memory_data = get_all_memory()
    total_adv = memory_data.get("total_advisories", 0)
    st.metric("Advisories Recorded", total_adv)

    advisories = memory_data.get("advisories", [])
    if advisories:
        st.markdown("**Recent Advisory Logs:**")
        for adv in advisories[:4]:
            t_level = adv.get("threat_level", "MODERATE")
            st.markdown(f"""
<div class="memory-card">
  <b>{adv.get('crop')} in {adv.get('location')}</b> ({adv.get('timestamp')})<br>
  Agent: <i>{adv.get('agent')}</i> · <span class="threat-tag threat-{t_level.lower()}">{t_level}</span><br>
  💡 {adv.get('advice_summary')[:100]}...
</div>
""", unsafe_allow_html=True)
    else:
        st.info("No farm advisories logged yet.")

    if st.button("🗑️ Clear Advisory Logs", key="clear_mem_btn"):
        clear_memory()
        st.success("Advisory logs reset!")
        st.rerun()


# ---------------------------------------------------------------
# MAIN PAGE: Header & Chat Interface
# ---------------------------------------------------------------
st.markdown('<div class="main-title">🌾 AgriShield AI Sentinel</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Autonomous Climate & Precision Agriculture Multi-Agent System<br>'
    '<b>Unit 3:</b> Farm Profile Memory &nbsp;|&nbsp; <b>Unit 4:</b> Multi-Agent Collaboration &nbsp;|&nbsp; <b>Reflection:</b> Risk Critic Audit</div>',
    unsafe_allow_html=True
)
st.markdown("---")

# ---------------------------------------------------------------
# Display Chat History
# ---------------------------------------------------------------
for entry in st.session_state.chat_history:
    role         = entry["role"]
    content      = entry["content"]
    steps        = entry.get("steps", [])
    active_agent = entry.get("active_agent")
    threat_level = entry.get("threat_level")

    if role == "user":
        st.markdown(
            f'<div class="user-bubble">👨‍🌾 <b>Farmer:</b> {content}</div>',
            unsafe_allow_html=True
        )

    elif role == "agent":
        if active_agent:
            st.markdown(agent_badge_html(active_agent, threat_level), unsafe_allow_html=True)

        if steps:
            with st.expander("🔍 Inspect Multi-Agent Execution & Agro-Telemetry", expanded=False):
                for step in steps:
                    if step["type"] == "tool_call":
                        st.markdown(
                            f'<div class="tool-box">🔧 Invoking Agro-Tool: <b>{step["tool"]}</b>'
                            f' with parameters: {step["input"]}</div>',
                            unsafe_allow_html=True
                        )
                    elif step["type"] == "tool_result":
                        st.markdown(
                            f'<div class="telemetry-box">📊 Real-Time Agro-Meteorology (Open-Meteo):\n{step["content"]}</div>',
                            unsafe_allow_html=True
                        )

        st.markdown(
            f'<div class="agent-bubble">{content}</div>',
            unsafe_allow_html=True
        )


# ---------------------------------------------------------------
# Quick Example Agronomic Queries
# ---------------------------------------------------------------
st.markdown("---")
with st.expander("💡 Recommended Agronomic Scenarios for Jury Demo", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**💧 Irrigation & Soil Water**")
        st.caption("• Should I run my borewell pump today?")
        st.caption("• What is the soil moisture and ET₀ status?")
    with col2:
        st.markdown("**🐛 Pest & Fungal Blight**")
        st.caption("• Will high humidity trigger fungal blight on my tomatoes?")
        st.caption("• Should I spray fungicide before the rain arrives?")
    with col3:
        st.markdown("**🚜 Spray Drift & Harvesting**")
        st.caption("• Is it safe to spray pesticide tomorrow morning?")
        st.caption("• Can I harvest my crop in the next 3 days?")


# ---------------------------------------------------------------
# Query Input
# ---------------------------------------------------------------
col_input, col_btn = st.columns([5, 1])

with col_input:
    user_query = st.text_input(
        label="Ask an agronomic question",
        placeholder=f"e.g. Should I run irrigation pumps for my {curr_profile.get('crop', 'Cotton')} crop today in {curr_profile.get('location', 'Pune')}?",
        label_visibility="collapsed",
        key="farmer_query_input"
    )

with col_btn:
    ask_btn = st.button("Consult AI 🚀", key="consult_btn")


# ---------------------------------------------------------------
# Execution Pipeline
# ---------------------------------------------------------------
if ask_btn and user_query.strip():
    # Append user question
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_query
    })

    # Build session message history for short-term memory
    session_messages = []
    for entry in st.session_state.chat_history:
        if entry["role"] == "user":
            session_messages.append(HumanMessage(content=entry["content"]))
        elif entry["role"] == "agent":
            session_messages.append(AIMessage(content=entry["content"]))

    with st.spinner("🌾 AgriShield agents coordinating telemetry, biology models, and risk audit..."):
        result = st.session_state.agent_app.invoke({
            "messages":       session_messages,
            "active_agent":   None,
            "memory_context": None,
            "crop_name":      curr_profile.get("crop", "Cotton"),
            "growth_stage":   curr_profile.get("growth_stage", "Flowering"),
            "farm_location":  curr_profile.get("location", "Pune"),
            "weather_data":   None,
            "threat_level":   None,
            "critic_notes":   None,
        })

    # Extract intermediate telemetry tool calls
    steps = []
    for msg in result["messages"]:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                steps.append({
                    "type":  "tool_call",
                    "tool":  tc["name"],
                    "input": tc["args"]
                })
        elif isinstance(msg, ToolMessage):
            steps.append({
                "type":    "tool_result",
                "content": msg.content
            })

    final_answer = result["messages"][-1].content
    active_agent = result.get("active_agent", "irrigation_sentinel")
    threat_level = result.get("threat_level", "MODERATE")

    st.session_state.chat_history.append({
        "role":         "agent",
        "content":      final_answer,
        "steps":        steps,
        "active_agent": active_agent,
        "threat_level": threat_level
    })

    st.rerun()
