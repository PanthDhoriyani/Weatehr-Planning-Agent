# 🌾 AgriShield AI — Autonomous Climate & Precision Agriculture Sentinel

An enterprise-grade Agentic AI system built with **LangGraph + LangChain + Groq + Open-Meteo Agricultural API** that provides real-time, autonomous agronomic decisions:
> *"Should I run my borewell pump today, or will tomorrow's rain save groundwater and electricity?"*  
> *"Will high atmospheric humidity cause fungal blight on my tomatoes?"*  
> *"Is the wind speed safe to spray pesticide without chemical drift?"*  
> *"Can I safely harvest my wheat crop over the next 3 days?"*

---

## 🏛️ Final Jury Architectural Highlights

| Extension | Concept | What It Does |
|---|---|---|
| **Unit 3** | **Long-Term Farm Profile Memory** | Persists farm state (Crop, Growth Stage, Soil Type, Location) & advisory audit log in `memory.json`. Injects farm context into reasoning prompts across sessions. |
| **Unit 4** | **Multi-Agent Specialist System** | Hierarchical Supervisor node routes queries to 3 domain specialists (`irrigation_sentinel`, `pest_disease_forecaster`, `harvest_spray_advisor`). |
| **Final Innovation** | **Reflection / Evaluator-Optimizer Loop** | A dedicated **Critic Node** audits sub-agent draft advice against environmental thresholds, assigns a **Crop Threat Index (LOW / MODERATE / SEVERE)**, and ensures safety guardrails before answering. |

---

## 🚀 How to Run

### 1. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate
```

### 2. Verify Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Ensure `.env` contains your Groq API key:
```env
GROQ_API_KEY=your_groq_key_here
```

### 4. Run the Streamlit Dashboard (Recommended for Jury Demo)
```bash
python -m streamlit run app.py
```

### 5. Run in Terminal (CLI Mode)
```bash
python main.py
```

---

## 📂 Project Structure
```
agentic_ai_jury_1/
├── agent/
│   ├── state.py         → AgentState (messages, active_agent, farm_profile, threat_level)
│   ├── tools.py         → Open-Meteo Agro API (ET₀, soil moisture, wind drift, humidity)
│   ├── nodes.py         → Supervisor + LLM Node + Sub-Agent Dispatch + Reflection Critic
│   ├── graph.py         → LangGraph Cyclic Graph with Evaluator-Optimizer
│   ├── memory.py        → Persistent Farm Profile & Advisory Memory (memory.json)
│   └── sub_agents.py    → 3 Domain Specialists + 1 Safety Critic Agent
├── memory.json          → Persistent Farm Memory & Advisory History
├── app.py               → Streamlit Dashboard with Farm Profile & Live Telemetry Inspector
├── main.py              → CLI runner for terminal demo
├── PRESENTATION_GUIDE.md→ Slide-by-slide jury script with Viva Q&A
├── requirements.txt
└── .env
```

---

## 🔄 Multi-Agent Workflow

```
                        [Farmer Query / Farm Profile]
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │    SUPERVISOR NODE    │  (Classifies farmer intent)
                         └───────────┬───────────┘
                                     │
                 ┌───────────────────┼───────────────────┐
                 ▼                   ▼                   ▼
       [💧 Irrigation]      [🐛 Pest/Disease]     [🚜 Harvest/Spray]
                 │                   │                   │
                 └───────────────────┼───────────────────┘
                                     ▼
                         ┌───────────────────────┐
                         │   LLM REASONING NODE  │  (Injects Farm Profile Memory)
                         └───────────┬───────────┘
                                     │
                                     ▼ (Invokes tool)
                         ┌───────────────────────┐
                         │    AGRI-TOOL NODE     │  (Open-Meteo Agro Telemetry)
                         │ • Soil moisture (0-7cm)│
                         │ • ET₀ Evapotranspiration
                         │ • Wind speed & humidity
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │  SUB-AGENT DISPATCH   │  (Generates domain-specific advice)
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │  SAFETY RISK CRITIC   │  (Evaluator-Optimizer: Audits thresholds)
                         │   [REFLECTION NODE]   │  (Computes Crop Threat Index: LOW/MOD/SEV)
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │      MEMORY SAVE      │  (Persists to memory.json)
                         └───────────┬───────────┘
                                     │
                                     ▼
                                   [END]
```

---

## 🌾 The 4 Sub-Agents

| Sub-Agent | Real-World Agronomic Rule | Trigger Keywords |
|---|---|---|
| 💧 **Irrigation Sentinel** | Evaluates **Soil Moisture** and **Evapotranspiration (ET₀)**. Pauses pumps if rain is imminent, saving groundwater & power. | water, irrigate, pump, drought, borewell, soil moisture |
| 🐛 **Pest & Disease Forecaster** | High humidity (>80%) + warm temp (22-30°C) triggers fungal spore germination. Recommends preventative sprays *before* rains. | pest, fungus, blight, rust, mildew, whitefly, worms |
| 🚜 **Harvest & Spray Advisor** | Wind > 15 km/h causes chemical drift; rain within 6h causes wash-off. Requires 3 dry days for grain harvesting. | spray, pesticide, fertilizer, wind drift, harvest, cutting |
| 🛡️ **Safety & Risk Critic** | Evaluates the draft advice, verifies environmental safety thresholds, and assigns the **Crop Threat Index**. | *Runs automatically via LangGraph reflection* |

---

## 🎯 Demo Questions for Jury

```
💧  "Should I run my irrigation pumps for cotton today in Pune?"
💧  "What is the soil moisture and evapotranspiration status?"
🐛  "High humidity is reported — will my tomatoes get early blight disease?"
🐛  "Should I apply fungicide before the rain arrives tomorrow?"
🚜  "Can I spray pesticide tomorrow morning in Nashik?"
🚜  "Is it safe to harvest my wheat crop over the next 3 days?"
```

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Agent Framework** | LangGraph (StateGraph with Evaluator-Optimizer loop) |
| **LLM Provider** | Groq Cloud (`openai/gpt-oss-120b`) |
| **Agricultural Telemetry** | Open-Meteo Agro & Soil API (Free, no key required) |
| **State Persistence** | `memory.json` (Dual-tier: Farm Profile + Advisory Log) |
| **User Interface** | Streamlit Dashboard with Telemetry Inspector |
