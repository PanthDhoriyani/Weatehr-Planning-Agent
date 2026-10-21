# Weather Planning Agent 🌧️

An autonomous AI agent built with **LangGraph + LangChain + Groq** that answers weather questions like:
> *"Should I carry an umbrella tomorrow in Pune?"*  
> *"What should I wear in Delhi tomorrow?"*  
> *"Is it a good day to travel to Goa?"*

---

## 🆕 Jury Extensions (Unit 3 + Unit 4)

| Extension | Concept | What It Does |
|---|---|---|
| **Unit 3** | Memory (Short-Term + Long-Term) | Remembers past cities & recommendations across sessions via `memory.json` |
| **Unit 4** | Multi-Agent System | Supervisor routes queries to 3 specialist sub-agents |

---

## How to Run

### 1. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate
```

### 2. Install dependencies (if setting up fresh)
```bash
pip install -r requirements.txt
```

### 3. Add your Groq API key
- Open the `.env` file
- Replace `your_groq_key_here` with your actual key
- Get a free key at: https://console.groq.com/keys

### 4. Run the Streamlit web app (recommended for jury demo)
```bash
python -m streamlit run app.py
```

### 5. OR run in terminal (CLI mode)
```bash
python main.py
```

---

## Project Structure
```
agentic_ai_jury_1/
├── venv/                → Local Virtual Environment
├── agent/
│   ├── state.py         → AgentState (messages + active_agent + memory fields)
│   ├── tools.py         → Weather tool (Open-Meteo API)
│   ├── nodes.py         → Supervisor + LLM node + Sub-Agent Dispatch
│   ├── graph.py         → LangGraph multi-agent graph
│   ├── memory.py        → [NEW] Long-Term Memory (reads/writes memory.json)
│   └── sub_agents.py    → [NEW] 3 Specialist Sub-Agents
├── memory.json          → [AUTO-CREATED] Persistent long-term memory store
├── app.py               → Streamlit UI with Memory Panel + Agent Activity
├── main.py              → CLI runner for terminal demo
├── requirements.txt
└── .env                 → API keys
```

---

## How the Agent Works

### Original Flow (Base)
1. **User asks a weather question** (e.g. *"Will it rain in Pune tomorrow?"*)
2. **LLM reads the question** and determines if it needs live weather data
3. **Agent invokes `get_weather_forecast` tool** → queries Open-Meteo API
4. **LLM reasons over the data** → delivers a clear recommendation
5. **Guardrails:** Off-topic questions (math, trivia) are politely rejected

### Extended Flow (Jury Extensions)

```
User Query
   │
   ▼
[SUPERVISOR NODE]  ←── Unit 4: decides which specialist handles this
   │
   ├──► 🌦️ Weather Agent     → "Will it rain?"
   ├──► 👗 Outfit Advisor     → "What to wear?"
   └──► ✈️ Travel Planner     → "Good day to travel?"
             │
             ▼
       [LLM Node]  ←── Unit 3: Long-Term Memory injected into system prompt
             │
             ▼
       [Tool Node] → get_weather_forecast (Open-Meteo API)
             │
             ▼
       [Sub-Agent Dispatch] → specialist gives focused answer
             │
             ▼
       [Memory Save]  ←── Unit 3: city + recommendation saved to memory.json
```

---

## Unit 3 — Memory System

| Memory Type | How | Where Visible |
|---|---|---|
| **Short-Term** | LangGraph message list (`operator.add`) | Agent reasoning steps |
| **Long-Term** | `memory.py` → `memory.json` on disk | 📚 Sidebar Memory Panel |

- Survives app restarts
- Injects "User previously asked about Pune" into LLM prompt
- Shows query count, last date, last recommendation per city
- Has a **Clear Memory** button in the sidebar

---

## Unit 4 — Multi-Agent System

| Sub-Agent | Trigger Keywords | Specialty |
|---|---|---|
| 🌦️ **Weather Agent** | rain, umbrella, forecast, weather | Plain weather forecasts |
| 👗 **Outfit Advisor** | wear, clothes, dress, outfit | Clothing recommendations |
| ✈️ **Travel Planner** | travel, trip, drive, go to, visit | Travel suitability |

The **Supervisor Node** classifies every query and activates the right sub-agent.  
The UI shows a color-coded badge on each response showing which agent handled it.

---

## Demo Questions for Jury

```
🌦️  "Will it rain in Pune tomorrow?"
🌦️  "Should I carry an umbrella in Mumbai?"
👗  "What should I wear tomorrow in Delhi?"
👗  "What clothes for rainy weather in Chennai?"
✈️  "Is it a good day to travel to Goa?"
✈️  "Can I go to Manali this weekend?"
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Agent Framework | LangGraph (StateGraph) |
| LLM | Groq Cloud — `openai/gpt-oss-120b` |
| Weather API | Open-Meteo (free, no key needed) |
| Memory Store | JSON file (built-in, no DB needed) |
| UI | Streamlit |
| Language | Python 3.10+ |
