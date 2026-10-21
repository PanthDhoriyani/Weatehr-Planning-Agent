"""
app.py — Weather Planning Agent: Extended Streamlit UI
--------------------------------------------------------
Original:  Chat interface with agent thinking steps
Extended:
  - Sidebar: 📚 Long-Term Memory panel (Unit 3)
  - Sidebar: 🤖 Agent Activity tracker showing active sub-agent (Unit 4)
  - Chat: Sub-agent badge on each response
"""

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from agent.graph import build_graph
from agent.memory import get_all_memory, clear_memory
from agent.sub_agents import SUB_AGENT_LABELS

# ---------------------------------------------------------------
# page config — must be first streamlit call
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Weather Planning Agent",
    page_icon="🌧️",
    layout="wide"
)

# ---------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    * { font-family: 'Inter', sans-serif; }

    /* overall background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }

    /* sidebar */
    [data-testid="stSidebar"] {
        background: rgba(255,255,255,0.04);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    /* title styling */
    .main-title {
        text-align: center;
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a8edea, #fed6e3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .sub-title {
        text-align: center;
        color: #aaa;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    /* chat bubble - user */
    .user-bubble {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0 8px 60px;
        font-size: 0.95rem;
    }

    /* chat bubble - agent */
    .agent-bubble {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.15);
        color: #e0e0e0;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 60px 8px 0;
        font-size: 0.95rem;
        backdrop-filter: blur(10px);
    }

    /* tool call / thinking box */
    .tool-box {
        background: rgba(255, 200, 0, 0.08);
        border-left: 3px solid #ffd700;
        padding: 8px 14px;
        border-radius: 0 8px 8px 0;
        margin: 6px 0;
        font-size: 0.82rem;
        color: #ffd700;
        font-family: monospace;
    }

    /* tool result box */
    .tool-result-box {
        background: rgba(0, 255, 136, 0.06);
        border-left: 3px solid #00ff88;
        padding: 8px 14px;
        border-radius: 0 8px 8px 0;
        margin: 6px 0;
        font-size: 0.82rem;
        color: #00ff88;
        font-family: monospace;
        white-space: pre-wrap;
    }

    /* input box */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 12px !important;
    }

    /* buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2, #667eea);
        transform: translateY(-1px);
    }

    /* sub-agent badge */
    .agent-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .badge-weather  { background: rgba(100,180,255,0.2); border: 1px solid #64b4ff; color: #64b4ff; }
    .badge-outfit   { background: rgba(255,150,200,0.2); border: 1px solid #ff96c8; color: #ff96c8; }
    .badge-travel   { background: rgba(100,255,180,0.2); border: 1px solid #64ffb4; color: #64ffb4; }
    .badge-off_topic{ background: rgba(255,100,100,0.2); border: 1px solid #ff6464; color: #ff6464; }

    /* memory card */
    .memory-card {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 10px;
        padding: 10px 14px;
        margin: 6px 0;
        font-size: 0.82rem;
        color: #ccc;
    }
    .memory-city {
        font-weight: 700;
        color: #a8edea;
    }

    hr { border-color: rgba(255,255,255,0.1); }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------
# Helper: badge HTML for sub-agent
# ---------------------------------------------------------------
def agent_badge_html(agent_key: str) -> str:
    label = SUB_AGENT_LABELS.get(agent_key, "🤖 Agent")
    badge_class_map = {
        "weather_agent":  "badge-weather",
        "outfit_advisor": "badge-outfit",
        "travel_planner": "badge-travel",
        "off_topic":      "badge-off_topic",
    }
    cls = badge_class_map.get(agent_key, "badge-weather")
    return f'<span class="agent-badge {cls}">{label}</span>'


# ---------------------------------------------------------------
# Session State
# ---------------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "agent_app" not in st.session_state:
    with st.spinner("Loading agent..."):
        st.session_state.agent_app = build_graph()


# ---------------------------------------------------------------
# SIDEBAR — Unit 3: Memory Panel + Unit 4: Agent Activity
# ---------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🤖 Multi-Agent System")
    st.caption("Unit 4 Extension — Active Sub-Agent")

    if st.session_state.chat_history:
        last_agent = None
        for entry in reversed(st.session_state.chat_history):
            if entry["role"] == "agent" and entry.get("active_agent"):
                last_agent = entry["active_agent"]
                break
        if last_agent:
            st.markdown(agent_badge_html(last_agent), unsafe_allow_html=True)
            label = SUB_AGENT_LABELS.get(last_agent, "Agent")
            st.caption(f"Last query handled by: **{label}**")
        else:
            st.caption("No queries yet.")
    else:
        st.caption("No queries yet.")

    st.markdown("---")

    # ── All 3 sub-agents info ─────────────────────────────
    st.markdown("**Available Sub-Agents:**")
    st.markdown("""
- 🌦️ **Weather Agent** — Rain & forecast queries  
- 👗 **Outfit Advisor** — What to wear  
- ✈️ **Travel Planner** — Trip suitability  
""")

    st.markdown("---")

    # ── Unit 3: Long-Term Memory Panel ───────────────────
    st.markdown("## 📚 Long-Term Memory")
    st.caption("Unit 3 Extension — Persists across sessions")

    memory_data = get_all_memory()

    if memory_data["total_queries"] == 0:
        st.info("No memory yet. Ask about a city!")
    else:
        st.metric("Total Queries", memory_data["total_queries"])
        if memory_data["last_active"]:
            st.caption(f"Last active: {memory_data['last_active']}")

        st.markdown("**Cities Remembered:**")
        for key, val in memory_data["cities"].items():
            st.markdown(f"""
<div class="memory-card">
  <span class="memory-city">{val['display_name']}</span><br>
  🔁 Asked <b>{val['query_count']}x</b> · Last: {val['last_queried'] or 'N/A'}<br>
  💬 <i>{val['last_recommendation'] or 'N/A'}</i>
</div>
""", unsafe_allow_html=True)

    if st.button("🗑️ Clear Memory", key="clear_mem_btn"):
        clear_memory()
        st.success("Memory cleared!")
        st.rerun()

    st.markdown("---")
    st.markdown("**How Memory Works:**")
    st.markdown("""
- **Short-Term**: Current conversation messages  
- **Long-Term**: Saved to `memory.json` (survives restarts)  
""")


# ---------------------------------------------------------------
# MAIN AREA — Header
# ---------------------------------------------------------------
st.markdown('<div class="main-title">🌧️ Weather Planning Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Powered by LangGraph + Multi-Agent System · '
    'Unit 3: Memory &nbsp;|&nbsp; Unit 4: Multi-Agent</div>',
    unsafe_allow_html=True
)
st.markdown("---")


# ---------------------------------------------------------------
# Display chat history
# ---------------------------------------------------------------
for entry in st.session_state.chat_history:
    role         = entry["role"]
    content      = entry["content"]
    steps        = entry.get("steps", [])
    active_agent = entry.get("active_agent")

    if role == "user":
        st.markdown(
            f'<div class="user-bubble">👤 {content}</div>',
            unsafe_allow_html=True
        )

    elif role == "agent":
        # show agent badge (Unit 4)
        if active_agent:
            st.markdown(agent_badge_html(active_agent), unsafe_allow_html=True)

        # show thinking steps
        if steps:
            with st.expander("🔍 See agent's thinking steps", expanded=False):
                for step in steps:
                    if step["type"] == "tool_call":
                        st.markdown(
                            f'<div class="tool-box">🔧 Calling tool: <b>{step["tool"]}</b>'
                            f' with input: {step["input"]}</div>',
                            unsafe_allow_html=True
                        )
                    elif step["type"] == "tool_result":
                        st.markdown(
                            f'<div class="tool-result-box">📊 Tool result:\n{step["content"]}</div>',
                            unsafe_allow_html=True
                        )

        st.markdown(
            f'<div class="agent-bubble">🤖 {content}</div>',
            unsafe_allow_html=True
        )


# ---------------------------------------------------------------
# Input area
# ---------------------------------------------------------------
st.markdown("---")

with st.expander("💡 Try these example questions"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🌦️ Weather Agent**")
        st.markdown("- Will it rain in Pune tomorrow?")
        st.markdown("- Should I carry an umbrella in Mumbai?")
    with col2:
        st.markdown("**👗 Outfit Advisor**")
        st.markdown("- What should I wear tomorrow in Delhi?")
        st.markdown("- What clothes for rainy weather in Chennai?")
    with col3:
        st.markdown("**✈️ Travel Planner**")
        st.markdown("- Good day to travel to Goa?")
        st.markdown("- Can I go to Manali this weekend?")

col_input, col_btn = st.columns([4, 1])

with col_input:
    user_question = st.text_input(
        label="Ask a question",
        placeholder="e.g. What should I wear tomorrow in Pune?",
        label_visibility="collapsed",
        key="user_input"
    )

with col_btn:
    ask_clicked = st.button("Ask 🚀", key="ask_btn")


# ---------------------------------------------------------------
# Process query
# ---------------------------------------------------------------
if ask_clicked and user_question.strip():

    # add user message to display history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_question
    })

    # ── Unit 3: Short-Term Memory ─────────────────────────────────
    # Rebuild the full message list from this session's chat history
    # so the LLM sees everything said so far (not just the latest msg).
    # This is short-term memory: in-context, within one session.
    from langchain_core.messages import AIMessage as AI_Msg
    session_messages = []
    for entry in st.session_state.chat_history:
        if entry["role"] == "user":
            session_messages.append(HumanMessage(content=entry["content"]))
        elif entry["role"] == "agent":
            session_messages.append(AI_Msg(content=entry["content"]))
    # ─────────────────────────────────────────────────────────────

    with st.spinner("🤔 Agent is thinking..."):
        result = st.session_state.agent_app.invoke({
            "messages":       session_messages,   # full history = short-term memory
            "active_agent":   None,
            "memory_context": None,
            "weather_data":   None,
        })

    # extract intermediate steps
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
    active_agent = result.get("active_agent", "weather_agent")

    st.session_state.chat_history.append({
        "role":         "agent",
        "content":      final_answer,
        "steps":        steps,
        "active_agent": active_agent,
    })

    st.rerun()

