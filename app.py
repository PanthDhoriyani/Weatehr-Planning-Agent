import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from agent.graph import build_graph

# ---------------------------------------------------------------
# page config — must be first streamlit call
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Weather Planning Agent",
    page_icon="🌧️",
    layout="centered"
)

# ---------------------------------------------------------------
# custom CSS to make it look nice
# ---------------------------------------------------------------
st.markdown("""
<style>
    /* overall background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }

    /* title styling */
    .main-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a8edea, #fed6e3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .sub-title {
        text-align: center;
        color: #aaa;
        font-size: 1rem;
        margin-bottom: 2rem;
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

    /* input box styling */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 12px !important;
    }

    /* button */
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

    /* divider */
    hr {
        border-color: rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------
# header
# ---------------------------------------------------------------
st.markdown('<div class="main-title">🌧️ Weather Planning Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Powered by LangGraph + Gemini · Ask anything about weather!</div>', unsafe_allow_html=True)
st.markdown("---")


# ---------------------------------------------------------------
# session state — store chat history so it persists on rerun
# ---------------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of (role, content, steps)

if "agent_app" not in st.session_state:
    # build the agent once and cache it
    with st.spinner("Loading agent..."):
        st.session_state.agent_app = build_graph()


# ---------------------------------------------------------------
# display previous chat messages
# ---------------------------------------------------------------
for entry in st.session_state.chat_history:
    role    = entry["role"]
    content = entry["content"]
    steps   = entry.get("steps", [])   # intermediate tool steps

    if role == "user":
        st.markdown(f'<div class="user-bubble">👤 {content}</div>', unsafe_allow_html=True)

    elif role == "agent":
        # show any intermediate steps (tool calls and results)
        if steps:
            with st.expander("🔍 See agent's thinking steps", expanded=False):
                for step in steps:
                    if step["type"] == "tool_call":
                        st.markdown(
                            f'<div class="tool-box">🔧 Calling tool: <b>{step["tool"]}</b> with input: {step["input"]}</div>',
                            unsafe_allow_html=True
                        )
                    elif step["type"] == "tool_result":
                        st.markdown(
                            f'<div class="tool-result-box">📊 Tool result:\n{step["content"]}</div>',
                            unsafe_allow_html=True
                        )

        st.markdown(f'<div class="agent-bubble">🤖 {content}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------
# input area at the bottom
# ---------------------------------------------------------------
st.markdown("---")

# example questions to show jury
with st.expander("💡 Try these example questions"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("- Should I carry an umbrella tomorrow in Pune?")
        st.markdown("- Will it rain in Mumbai tomorrow?")
        st.markdown("- Is it going to pour in Delhi?")
    with col2:
        st.markdown("- Do I need a raincoat tomorrow in Chennai?")
        st.markdown("- What's the weather like tomorrow in Bangalore?")
        st.markdown("- What's the capital of France? *(will be rejected)*")

# text input + button
col_input, col_btn = st.columns([4, 1])

with col_input:
    user_question = st.text_input(
        label="Ask a question",
        placeholder="e.g. Should I carry an umbrella tomorrow in Pune?",
        label_visibility="collapsed",
        key="user_input"
    )

with col_btn:
    ask_clicked = st.button("Ask 🚀", key="ask_btn")


# ---------------------------------------------------------------
# when user clicks Ask (or presses Enter)
# ---------------------------------------------------------------
if ask_clicked and user_question.strip():

    # add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_question
    })

    # run the agent
    with st.spinner("🤔 Agent is thinking..."):
        result = st.session_state.agent_app.invoke({
            "messages": [HumanMessage(content=user_question)]
        })

    # extract intermediate steps (tool calls + tool results)
    steps = []
    for msg in result["messages"]:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            # LLM decided to call a tool
            for tc in msg.tool_calls:
                steps.append({
                    "type":  "tool_call",
                    "tool":  tc["name"],
                    "input": tc["args"]
                })
        elif isinstance(msg, ToolMessage):
            # the tool returned a result
            steps.append({
                "type":    "tool_result",
                "content": msg.content
            })

    # the last AIMessage with no tool_calls is the final answer
    final_answer = result["messages"][-1].content

    # add agent response to history
    st.session_state.chat_history.append({
        "role":    "agent",
        "content": final_answer,
        "steps":   steps
    })

    # rerun to refresh the UI with the new messages
    st.rerun()
