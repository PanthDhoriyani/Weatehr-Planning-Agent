# Weather Planning Agent 🌧️

A simple AI agent built with **LangGraph + LangChain + Groq** that answers weather questions like:
> *"Should I carry an umbrella tomorrow in Pune?"*

---

## How to Run

### 1. (Optional) Activate Virtual Environment
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
├── venv/           → Local Virtual Environment (packages installed here)
├── agent/
│   ├── state.py    → AgentState definition (LangGraph state)
│   ├── tools.py    → Weather tool (Open-Meteo API)
│   ├── nodes.py    → LLM node + system prompt & guardrails
│   └── graph.py    → LangGraph graph assembly (nodes + conditional edges)
├── app.py          → Streamlit web UI with reasoning inspector
├── main.py         → CLI runner for terminal demo
├── requirements.txt
└── .env            → API keys
```

---

## How the Agent Works
1. **User asks a weather question** (e.g. *"Should I carry an umbrella tomorrow in Pune?"*)
2. **LLM reads the question** and determines if it needs live weather data
3. **Agent invokes `get_weather_forecast` tool** to query Open-Meteo Geocoding & Forecast APIs
4. **LLM reasons over the returned data** (precipitation probability, weather condition) to deliver a clear recommendation
5. **Guardrails:** If the question is off-topic (e.g. math, general trivia), the agent politely refuses
