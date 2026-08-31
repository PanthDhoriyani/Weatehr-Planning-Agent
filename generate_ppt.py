import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # Set 16:9 widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6]

    # Color Palette (Modern Dark / Tech Gradient aesthetic)
    BG_DARK = RGBColor(15, 23, 42)       # Slate 900
    BG_CARD = RGBColor(30, 41, 59)       # Slate 800
    BG_CARD_ACC = RGBColor(51, 65, 85)   # Slate 700
    ACCENT_CYAN = RGBColor(56, 189, 248)  # Cyan 400
    ACCENT_BLUE = RGBColor(96, 165, 250)  # Blue 400
    ACCENT_GREEN = RGBColor(74, 222, 128) # Green 400
    ACCENT_ORANGE = RGBColor(251, 146, 60)# Orange 400
    TEXT_WHITE = RGBColor(248, 250, 252)  # White
    TEXT_MUTED = RGBColor(148, 163, 184)  # Slate 400

    def add_header(slide, category, title, subtitle=None):
        # Category / Kicker
        tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
        tf_cat = tb_cat.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_right = tf_cat.margin_top = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_CYAN
        p_cat.font.name = "Arial"

        # Main Title
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.6))
        tf_title = tb_title.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_right = tf_title.margin_top = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE
        p_title.font.name = "Arial"

        if subtitle:
            tb_sub = slide.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.7), Inches(0.35))
            tf_sub = tb_sub.text_frame
            tf_sub.word_wrap = True
            tf_sub.margin_left = tf_sub.margin_right = tf_sub.margin_top = tf_sub.margin_bottom = 0
            p_sub = tf_sub.paragraphs[0]
            p_sub.text = subtitle
            p_sub.font.size = Pt(13)
            p_sub.font.color.rgb = TEXT_MUTED
            p_sub.font.name = "Arial"

    def set_slide_bg(slide):
        bg_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5)
        )
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = BG_DARK
        bg_shape.line.fill.background()
        return bg_shape

    def create_card(slide, left, top, width, height, bg_color=BG_CARD, border_color=None):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1.5)
        else:
            card.line.fill.background()
        return card

    # ==========================================
    # SLIDE 1: TITLE SLIDE
    # ==========================================
    s1 = prs.slides.add_slide(blank_slide_layout)
    set_slide_bg(s1)

    # Accent decorative banner
    create_card(s1, Inches(0.8), Inches(1.5), Inches(11.733), Inches(4.8), bg_color=BG_CARD, border_color=ACCENT_CYAN)

    tb_t = s1.shapes.add_textbox(Inches(1.2), Inches(1.9), Inches(11.0), Inches(2.2))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    
    p0 = tf_t.paragraphs[0]
    p0.text = "AGENTIC AI & STATEGRAPH ARCHITECTURES"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = ACCENT_CYAN

    p1 = tf_t.add_paragraph()
    p1.text = "Autonomous Weather Planning Agent"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p1.space_before = Pt(8)

    p2 = tf_t.add_paragraph()
    p2.text = "A Stateful ReAct Agent with Tool-Augmented LLM Reasoning & Live Meteorological Grounding"
    p2.font.size = Pt(16)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_before = Pt(10)

    # Info pills
    pill_data = [
        ("Core Paradigm", "Agentic Tool Calling (ReAct)"),
        ("Orchestration", "LangGraph & LangChain"),
        ("Inference Engine", "Groq Cloud (Fast LLMs)"),
        ("Live Grounding", "Open-Meteo Weather & Geocoding API")
    ]
    pill_w = Inches(2.55)
    for i, (label, val) in enumerate(pill_data):
        pl = Inches(1.2) + i * Inches(2.7)
        create_card(s1, pl, Inches(4.4), pill_w, Inches(1.4), bg_color=BG_CARD_ACC)
        tb_p = s1.shapes.add_textbox(pl + Inches(0.15), Inches(4.5), pill_w - Inches(0.3), Inches(1.2))
        tf_p = tb_p.text_frame
        tf_p.word_wrap = True
        pp1 = tf_p.paragraphs[0]
        pp1.text = label.upper()
        pp1.font.size = Pt(10)
        pp1.font.color.rgb = ACCENT_CYAN
        pp1.font.bold = True
        pp2 = tf_p.add_paragraph()
        pp2.text = val
        pp2.font.size = Pt(12)
        pp2.font.color.rgb = TEXT_WHITE
        pp2.font.bold = True
        pp2.space_before = Pt(4)

    s1.notes_slide.notes_text_frame.text = (
        "Good morning / afternoon Professor. Today I am presenting our project: The Autonomous Weather Planning Agent. "
        "Before diving into the code demonstration, this presentation covers the comprehensive theoretical foundations "
        "of Agentic AI, state machine orchestration using LangGraph, dynamic tool calling, and live data grounding."
    )

    # ==========================================
    # SLIDE 2: THE PROBLEM & MOTIVATION
    # ==========================================
    s2 = prs.slides.add_slide(blank_slide_layout)
    set_slide_bg(s2)
    add_header(s2, "Theoretical Motivation", "Why Traditional LLMs Fail at Real-World Planning", "Understanding the fundamental limitations of standalone generative language models")

    cols_s2 = [
        ("1. Knowledge Cutoff & Staleness", 
         "• Pretrained LLMs have static parameter weights freeze-dried at training time.\n• Cannot know today's or tomorrow's weather conditions anywhere in the world.\n• Predictions regarding dynamic real-world state are fundamentally impossible without external augmentation.",
         ACCENT_ORANGE),
        ("2. Hallucination of Dynamic Facts", 
         "• Generative models optimize for textual probability, not factual truth.\n• When asked 'Will it rain tomorrow in Mumbai?', a standard LLM will fabricate plausible-sounding temperatures and precipitation probabilities.",
         ACCENT_CYAN),
        ("3. Inability to Execute Actions", 
         "• Standard conversational models only output tokens.\n• They lack agency: they cannot query databases, invoke REST endpoints, parse responses, or maintain verifiable execution loops.",
         ACCENT_GREEN)
    ]
    for i, (title, body, acc) in enumerate(cols_s2):
        l = Inches(0.8) + i * Inches(3.95)
        create_card(s2, l, Inches(1.8), Inches(3.75), Inches(5.0), bg_color=BG_CARD)
        create_card(s2, l, Inches(1.8), Inches(3.75), Inches(0.1), bg_color=acc)
        tb = s2.shapes.add_textbox(l + Inches(0.2), Inches(2.1), Inches(3.35), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(15)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE
        
        p_b = tf.add_paragraph()
        p_b.text = body
        p_b.font.size = Pt(12)
        p_b.font.color.rgb = TEXT_MUTED
        p_b.space_before = Pt(12)

    s2.notes_slide.notes_text_frame.text = (
        "Theoretical basis: Pretrained LLMs are closed-world probabilistic token predictors. "
        "For real-world physical problems like weather planning, we must transition from pure generation to grounded agentic systems."
    )

    # ==========================================
    # SLIDE 3: WHAT IS AGENTIC AI?
    # ==========================================
    s3 = prs.slides.add_slide(blank_slide_layout)
    set_slide_bg(s3)
    add_header(s3, "Conceptual Foundation", "Agentic AI vs. Traditional Chatbots", "The paradigm shift from passive text completion to autonomous action loops")

    # Left: Traditional Chatbot
    create_card(s3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), bg_color=BG_CARD)
    tb_c1 = s3.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.5))
    tf_c1 = tb_c1.text_frame
    tf_c1.word_wrap = True
    p = tf_c1.paragraphs[0]
    p.text = "Traditional Chatbots (Passive LLMs)"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = ACCENT_ORANGE

    p = tf_c1.add_paragraph()
    p.text = "• Model: Single input prompt -> Single text completion.\n• Interaction: Zero environment feedback; purely reactive.\n• Knowledge: Bound strictly to internal parameters.\n• Decision Making: No multi-step reasoning or verification.\n• Action Space: None (text-only generation)."
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(12)

    # Right: Agentic AI
    create_card(s3, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), bg_color=BG_CARD, border_color=ACCENT_CYAN)
    tb_c2 = s3.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.5))
    tf_c2 = tb_c2.text_frame
    tf_c2.word_wrap = True
    p = tf_c2.paragraphs[0]
    p.text = "Agentic AI Systems (Autonomous Loop)"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    p = tf_c2.add_paragraph()
    p.text = "• Model: Autonomous perception, reasoning, and tool use.\n• Feedback Loop: Perceive -> Plan -> Act (Tools) -> Observe -> Conclude.\n• Grounding: Integrates deterministic live APIs with stochastic reasoning.\n• State Awareness: Retains evolving state across execution steps.\n• Action Space: Arbitrary programmatic tools & external APIs."
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(12)

    s3.notes_slide.notes_text_frame.text = (
        "Explain the fundamental difference between passive LLM generation and autonomous agents. "
        "An agent operates in an environment, utilizes tools to perceive external state, and executes goal-oriented plans."
    )

    # ==========================================
    # SLIDE 4: THE ReAct PARADIGM
    # ==========================================
    s4 = prs.slides.add_slide(blank_slide_layout)
    set_slide_bg(s4)
    add_header(s4, "Reasoning Architecture", "The ReAct Theoretical Framework: Synergizing Reasoning & Acting", "Pioneered by Yao et al. (Google Brain / Princeton) for grounded problem solving")

    # Flow Cards
    steps = [
        ("1. THOUGHT", "LLM analyzes user query, identifies intent, recognizes missing external data (e.g. 'I need tomorrow's weather in Tokyo').", ACCENT_BLUE),
        ("2. ACTION", "LLM selects a registered tool ('get_weather_forecast') and formats structured JSON parameters ({'city': 'Tokyo'}).", ACCENT_CYAN),
        ("3. OBSERVATION", "Deterministic environment executes API call; parses coordinates & WMO meteorological metrics back to agent state.", ACCENT_GREEN),
        ("4. SYNTHESIS", "LLM reasons over real metrics (Rain 85%, Rain 4.2mm) to formulate actionable recommendations ('Carry an umbrella!').", ACCENT_ORANGE)
    ]
    for i, (title, desc, color) in enumerate(steps):
        left = Inches(0.8) + i * Inches(2.95)
        create_card(s4, left, Inches(1.8), Inches(2.8), Inches(4.9), bg_color=BG_CARD)
        create_card(s4, left, Inches(1.8), Inches(2.8), Inches(0.45), bg_color=color)
        
        tb = s4.shapes.add_textbox(left + Inches(0.15), Inches(1.85), Inches(2.5), Inches(0.35))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = BG_DARK

        tb_b = s4.shapes.add_textbox(left + Inches(0.15), Inches(2.4), Inches(2.5), Inches(4.0))
        tf_b = tb_b.text_frame
        tf_b.word_wrap = True
        pb = tf_b.paragraphs[0]
        pb.text = desc
        pb.font.size = Pt(12)
        pb.font.color.rgb = TEXT_WHITE
        pb.space_before = Pt(6)

    s4.notes_slide.notes_text_frame.text = (
        "ReAct stands for Reason + Act. Instead of trying to guess an answer, the model interleaves thought reasoning traces "
        "with concrete API actions, updating its internal observation context before delivering a verified response."
    )

    # ==========================================
    # SLIDE 5: STATEGRAPH COMPUTATION (LANGGRAPH)
    # ==========================================
    s5 = prs.slides.add_slide(blank_slide_layout)
    set_slide_bg(s5)
    add_header(s5, "Orchestration Layer", "Stateful Graph Computation with LangGraph", "Why state machines and cyclic graphs are required for robust agent orchestration")

    # Left: State Machine Concepts
    create_card(s5, Inches(0.8), Inches(1.8), Inches(6.0), Inches(5.0), bg_color=BG_CARD)
    tb_sg = s5.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.6), Inches(4.5))
    tf_sg = tb_sg.text_frame
    tf_sg.word_wrap = True
    p = tf_sg.paragraphs[0]
    p.text = "Key StateGraph Mathematical Principles"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    p = tf_sg.add_paragraph()
    p.text = (
        "• State as Single Source of Truth:\n"
        "  Every step operates on an immutable TypedDict state schema: `AgentState`.\n\n"
        "• Reducer Semantics (`operator.add`):\n"
        "  Message histories are monotonically accumulated rather than overwritten.\n\n"
        "• Cyclic Execution Topology:\n"
        "  Unlike rigid linear pipelines (DAGs), agents require cyclic loops where tool results feed back into the LLM for re-evaluation.\n\n"
        "• Deterministic Routing:\n"
        "  Conditional edges inspect tool call existence to decide between loop continuation or graph termination (`END`)."
    )
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(8)

    # Right: Graph Structure in Code
    create_card(s5, Inches(7.1), Inches(1.8), Inches(5.4), Inches(5.0), bg_color=BG_CARD, border_color=ACCENT_BLUE)
    tb_diag = s5.shapes.add_textbox(Inches(7.3), Inches(2.0), Inches(5.0), Inches(4.5))
    tf_diag = tb_diag.text_frame
    tf_diag.word_wrap = True
    p = tf_diag.paragraphs[0]
    p.text = "Graph Topology in Our Implementation"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    p = tf_diag.add_paragraph()
    p.text = (
        "┌──────────────────────────────┐\n"
        "│       START / ENTRY          │\n"
        "└──────────────┬───────────────┘\n"
        "               │\n"
        "               ▼\n"
        "       ┌───────────────┐\n"
        "       │   LLM Node    │ ◄──────────┐\n"
        "       └───────┬───────┘            │\n"
        "               │ (Conditional Edge) │\n"
        "         [Tool Called?]             │\n"
        "         /            \\             │\n"
        "     YES/              \\NO          │\n"
        "       ▼                ▼           │\n"
        "┌─────────────┐     ┌────────┐      │\n"
        "│  Tool Node  │────►│  END   │      │\n"
        "└─────────────┘     └────────┘ (Feed Result)"
    )
    p.font.size = Pt(11)
    p.font.color.rgb = ACCENT_CYAN
    p.font.name = "Courier New"
    p.space_before = Pt(8)

    s5.notes_slide.notes_text_frame.text = (
        "Highlight the graph structure: Entry point is the LLM node. Conditional edge checks if the LLM output contains tool calls. "
        "If yes, routes to ToolNode; ToolNode executes and loops back to LLM. If no tool calls, it routes directly to END."
    )

    # ==========================================
    # SLIDE 6: TOOL CALLING & API GROUNDING
    # ==========================================
    s6 = prs.slides.add_slide(blank_slide_layout)
    set_slide_bg(s6)
    add_header(s6, "Deterministic Grounding", "2-Stage Meteorological Tool Pipeline", "Bridging natural language user queries to precise geospatial and atmospheric data")

    boxes_s6 = [
        ("Step 1: Geocoding Resolution", "User queries 'Paris', 'Ahmedabad', or 'Tokyo'.\nAPI: `geocoding-api.open-meteo.com`\nTranslates ambiguous named entities into exact WGS84 Latitude & Longitude coordinates with fallback error handling.", ACCENT_BLUE),
        ("Step 2: Live Forecast Ingestion", "API: `api.open-meteo.com/v1/forecast`\nFetches 2-day daily aggregates: Max/Min Temp (°C), Precipitation Probability (%), Precipitation Sum (mm), and WMO Weathercode.", ACCENT_CYAN),
        ("Step 3: WMO Standard Code Decoding", "Maps standardized numeric WMO (World Meteorological Organization) codes (e.g., Code 65 = Heavy Rain, Code 95 = Thunderstorm) to descriptive semantics and icons.", ACCENT_GREEN),
        ("Step 4: LLM Context Augmentation", "Tool formats structured, deterministic summary string back into `AgentState['messages']` as a `ToolMessage` for high-level decision reasoning.", ACCENT_ORANGE)
    ]
    for i, (title, desc, acc) in enumerate(boxes_s6):
        x = Inches(0.8) if i % 2 == 0 else Inches(6.8)
        y = Inches(1.8) if i < 2 else Inches(4.4)
        create_card(s6, x, y, Inches(5.7), Inches(2.4), bg_color=BG_CARD)
        create_card(s6, x, y, Inches(0.1), Inches(2.4), bg_color=acc)
        tb = s6.shapes.add_textbox(x + Inches(0.25), y + Inches(0.15), Inches(5.3), Inches(2.1))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MUTED
        p2.space_before = Pt(6)

    s6.notes_slide.notes_text_frame.text = (
        "Explain that the tool is a 2-step pipeline: First geocoding to resolve coordinates, "
        "second Open-Meteo weather endpoint to pull forecast metrics, and third standard WMO code mapping."
    )

    # ==========================================
    # SLIDE 7: GUARDRAILS & INTENT CLASSIFICATION
    # ==========================================
    s7 = prs.slides.add_slide(blank_slide_layout)
    set_slide_bg(s7)
    add_header(s7, "Agent Safety & Boundaries", "System Prompt Engineering & Guardrail Governance", "Preventing prompt injection, out-of-domain drift, and enforcing single-domain reliability")

    create_card(s7, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0), bg_color=BG_CARD)
    tb_g1 = s7.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tf_g1 = tb_g1.text_frame
    tf_g1.word_wrap = True
    p = tf_g1.paragraphs[0]
    p.text = "In-Scope vs. Out-of-Scope Classification"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p = tf_g1.add_paragraph()
    p.text = (
        "✅ ALLOWED IN-DOMAIN QUERIES:\n"
        "• Direct: 'Will it rain tomorrow in Delhi?'\n"
        "• Implicit Planning: 'Should I carry an umbrella tomorrow?'\n"
        "• Activity Planning: 'Can I take my bike to work tomorrow?'\n"
        "• Clothing Advice: 'Do I need a heavy jacket in London?'\n\n"
        "❌ STRICTLY REJECTED OUT-OF-DOMAIN:\n"
        "• General knowledge ('Capital of France?')\n"
        "• Math problems ('Solve 2+2')\n"
        "• Coding & debugging queries\n"
        "• Sports scores, entertainment, etc."
    )
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(8)

    create_card(s7, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), bg_color=BG_CARD)
    tb_g2 = s7.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tf_g2 = tb_g2.text_frame
    tf_g2.word_wrap = True
    p = tf_g2.paragraphs[0]
    p.text = "Guardrail Architecture Mechanisms"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_ORANGE
    p = tf_g2.add_paragraph()
    p.text = (
        "1. Contextual Boundary Prompting:\n"
        "   System prompt establishes strict role identity before any user token is evaluated.\n\n"
        "2. Deterministic Fallback Response:\n"
        "   If out-of-domain, agent outputs a standardized polite refusal without invoking expensive API tools.\n\n"
        "3. Low Temperature Sampling (T=0.3):\n"
        "   Minimizes hallucinations and guarantees adherence to rule boundaries.\n\n"
        "4. Output Contract Enforcement:\n"
        "   Requires clear YES/NO recommendation + data-backed reason."
    )
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(8)

    s7.notes_slide.notes_text_frame.text = (
        "Explain how the agent acts responsibly: It understands implicit weather queries while refusing unrelated queries "
        "to maintain domain specialization and prevent compute misuse."
    )

    # ==========================================
    # SLIDE 8: END-TO-END EXECUTION TRACE
    # ==========================================
    s8 = prs.slides.add_slide(blank_slide_layout)
    set_slide_bg(s8)
    add_header(s8, "Traceability & Execution", "End-to-End Agent Execution Trace", "Step-by-step state transition during a real user interaction")

    steps_trace = [
        ("Step 1: User Input", "User: 'Do I need an umbrella in Pune tomorrow?'", ACCENT_CYAN),
        ("Step 2: LLM Reasoning Node", "LLM determines Pune weather is required. Emits tool call: get_weather_forecast(city='Pune')", ACCENT_BLUE),
        ("Step 3: Tool Execution Node", "Tool runs geocoding (18.52°N, 73.85°E) -> Open-Meteo API -> Returns: Rain Chance 80%, 12mm rain, Moderate rain showers", ACCENT_GREEN),
        ("Step 4: LLM Synthesis Node", "LLM reads ToolMessage -> Decides umbrella is necessary -> Generates final synthesis", ACCENT_ORANGE),
        ("Step 5: User Presentation", "Output: 'Yes, carry an umbrella! Pune will have an 80% chance of rain with moderate rain showers tomorrow.'", ACCENT_CYAN)
    ]
    for i, (st, desc, c) in enumerate(steps_trace):
        y = Inches(1.8) + i * Inches(1.0)
        create_card(s8, Inches(0.8), y, Inches(11.733), Inches(0.85), bg_color=BG_CARD)
        create_card(s8, Inches(0.8), y, Inches(2.5), Inches(0.85), bg_color=c)
        
        tb1 = s8.shapes.add_textbox(Inches(0.9), y + Inches(0.2), Inches(2.3), Inches(0.5))
        tf1 = tb1.text_frame
        p1 = tf1.paragraphs[0]
        p1.text = st
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = BG_DARK

        tb2 = s8.shapes.add_textbox(Inches(3.5), y + Inches(0.12), Inches(8.8), Inches(0.65))
        tf2 = tb2.text_frame
        tf2.word_wrap = True
        p2 = tf2.paragraphs[0]
        p2.text = desc
        p2.font.size = Pt(12)
        p2.font.color.rgb = TEXT_WHITE

    s8.notes_slide.notes_text_frame.text = (
        "Walk the teacher through this concrete execution trace showing how the state progresses from "
        "User Message -> AIMessage (Tool Call) -> ToolMessage (Weather Data) -> AIMessage (Final Output)."
    )

    # ==========================================
    # SLIDE 9: TECHNOLOGY STACK & ARCHITECTURE
    # ==========================================
    s9 = prs.slides.add_slide(blank_slide_layout)
    set_slide_bg(s9)
    add_header(s9, "Technical Stack", "Core Components & Software Architecture", "Modular, decoupled engineering stack optimized for low latency and high reliability")

    tech_cards = [
        ("Orchestration Framework", "LangGraph & LangChain Core", "Manages cyclic StateGraph, TypedDict state reducers, conditional edges, and tool node binding.", ACCENT_CYAN),
        ("Inference Acceleration", "Groq Cloud API (LPU Inference)", "Ultra-low-latency LLM inference (~500 tokens/sec) enabling instantaneous conversational agent loops.", ACCENT_BLUE),
        ("Weather & Geospatial Grounding", "Open-Meteo REST Suite", "High-resolution global weather forecast APIs and WGS84 geocoding without proprietary API key bottlenecks.", ACCENT_GREEN),
        ("User Experience / Interface", "Streamlit Reactive UI", "Interactive web application displaying step-by-step thinking traces, status chips, weather metrics cards, and chat history.", ACCENT_ORANGE)
    ]
    for i, (cat, title, desc, acc) in enumerate(tech_cards):
        l = Inches(0.8) + i * Inches(2.95)
        create_card(s9, l, Inches(1.8), Inches(2.8), Inches(5.0), bg_color=BG_CARD)
        create_card(s9, l, Inches(1.8), Inches(2.8), Inches(0.1), bg_color=acc)
        
        tb = s9.shapes.add_textbox(l + Inches(0.15), Inches(2.1), Inches(2.5), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = cat.upper()
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = acc

        p2 = tf.add_paragraph()
        p2.text = title
        p2.font.size = Pt(14)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_WHITE
        p2.space_before = Pt(4)

        p3 = tf.add_paragraph()
        p3.text = desc
        p3.font.size = Pt(12)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(10)

    s9.notes_slide.notes_text_frame.text = (
        "Explain the technology stack choices: LangGraph for state management, Groq for sub-second inference, "
        "Open-Meteo for high precision meteorological data, and Streamlit for dynamic visualization."
    )

    # ==========================================
    # SLIDE 10: CHALLENGES & ENGINEERING SOLUTIONS
    # ==========================================
    s10 = prs.slides.add_slide(blank_slide_layout)
    set_slide_bg(s10)
    add_header(s10, "Engineering Rigor", "Technical Challenges & Applied Solutions", "Architectural hurdles encountered during development and how they were resolved")

    challenges = [
        ("Challenge 1: Tool Schema Adherence", "LLMs sometimes produce malformed JSON or pass stringified numbers.", "Solution: Utilized LangChain `@tool` decorator with type annotations and Pydantic schema validation under the hood.", ACCENT_ORANGE),
        ("Challenge 2: Multi-step Cyclic Loops", "Preventing infinite execution loops if tool returns an error or ambiguous city.", "Solution: Implemented LangGraph conditional edge routing and explicit tool error strings that guide the LLM to recover gracefully.", ACCENT_CYAN),
        ("Challenge 3: Ambiguous User Intention", "Handling implicit questions like 'Can I ride my bike?' without explicit mention of rain.", "Solution: System prompt contextualization instructing the model to recognize indirect outdoor activity queries as weather queries.", ACCENT_GREEN)
    ]
    for i, (ch, prb, sol, acc) in enumerate(challenges):
        l = Inches(0.8) + i * Inches(3.95)
        create_card(s10, l, Inches(1.8), Inches(3.75), Inches(5.0), bg_color=BG_CARD)
        create_card(s10, l, Inches(1.8), Inches(3.75), Inches(0.1), bg_color=acc)
        
        tb = s10.shapes.add_textbox(l + Inches(0.2), Inches(2.1), Inches(3.35), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = ch
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        p2 = tf.add_paragraph()
        p2.text = "Problem:\n" + prb
        p2.font.size = Pt(12)
        p2.font.color.rgb = TEXT_MUTED
        p2.space_before = Pt(8)

        p3 = tf.add_paragraph()
        p3.text = sol
        p3.font.size = Pt(12)
        p3.font.bold = True
        p3.font.color.rgb = ACCENT_CYAN
        p3.space_before = Pt(12)

    s10.notes_slide.notes_text_frame.text = (
        "Reviewing the key engineering challenges shows deep mastery of the topic to your professor: "
        "mention schema enforcement, graph cycles, and semantic prompt conditioning."
    )

    # ==========================================
    # SLIDE 11: FUTURE SCOPE & EXTENSIONS
    # ==========================================
    s11 = prs.slides.add_slide(blank_slide_layout)
    set_slide_bg(s11)
    add_header(s11, "Future Roadmap", "Scalability & Multi-Agent Evolution", "Transforming single-agent workflows into enterprise multi-agent planning systems")

    future_items = [
        ("Multi-Agent Collaboration", "Deploying specialized sub-agents (e.g., Clothing Advisor Agent, Travel Router Agent, Calendar Agent) coordinated by a Supervisor Agent.", ACCENT_CYAN),
        ("Personalized RAG & Memory", "Storing user preferences (e.g., commute type, cold tolerance) in a vector database (e.g. Chroma/Pinecone) for custom recommendations.", ACCENT_BLUE),
        ("Proactive Push Notifications", "Cron-scheduled background monitors that send proactive Telegram/WhatsApp alerts when rain probability exceeds threshold.", ACCENT_GREEN),
        ("Multi-Modal Satellite Ingestion", "Incorporating vision models to analyze Doppler radar and satellite cloud imagery alongside numeric tabular forecasts.", ACCENT_ORANGE)
    ]
    for i, (title, desc, acc) in enumerate(future_items):
        x = Inches(0.8) if i % 2 == 0 else Inches(6.8)
        y = Inches(1.8) if i < 2 else Inches(4.4)
        create_card(s11, x, y, Inches(5.7), Inches(2.4), bg_color=BG_CARD)
        create_card(s11, x, y, Inches(0.1), Inches(2.4), bg_color=acc)
        tb = s11.shapes.add_textbox(x + Inches(0.25), y + Inches(0.15), Inches(5.3), Inches(2.1))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MUTED
        p2.space_before = Pt(6)

    s11.notes_slide.notes_text_frame.text = (
        "Conclude with future scope: Multi-agent hierarchies, long-term user memory, proactive notifications, and multi-modal radar analysis."
    )

    # ==========================================
    # SLIDE 12: CONCLUSION & SUMMARY
    # ==========================================
    s12 = prs.slides.add_slide(blank_slide_layout)
    set_slide_bg(s12)
    add_header(s12, "Summary", "Key Takeaways & Conclusion", "Demonstrated mastery of Agentic AI, LangGraph state machines, and real-time grounding")

    create_card(s12, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.8), bg_color=BG_CARD, border_color=ACCENT_CYAN)
    tb_c = s12.shapes.add_textbox(Inches(1.2), Inches(2.1), Inches(11.0), Inches(4.2))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    
    p = tf_c.paragraphs[0]
    p.text = "Summary of Theoretical & Practical Achievements"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    takeaways = [
        "1. Bridged the LLM Knowledge Gap: Transformed a static LLM into an active, grounded meteorological reasoning agent.",
        "2. Formalized State Machine Orchestration: Replaced brittle prompt chains with LangGraph's robust, cyclic StateGraph architecture.",
        "3. Implemented Strict Domain Governance: Engineered system guardrails that prevent hallucination and maintain clear operational boundaries.",
        "4. Real-time Reactive Experience: Integrated sub-second Groq inference with a Streamlit interface for transparent agent introspection."
    ]
    for t in takeaways:
        p = tf_c.add_paragraph()
        p.text = t
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.space_before = Pt(12)

    p_end = tf_c.add_paragraph()
    p_end.text = "Thank You! Ready for Live Code Demonstration & Q&A."
    p_end.font.size = Pt(15)
    p_end.font.bold = True
    p_end.font.color.rgb = ACCENT_GREEN
    p_end.space_before = Pt(20)

    s12.notes_slide.notes_text_frame.text = (
        "Deliver the final concluding remarks and transition smoothly to the live Streamlit code demonstration!"
    )

    output_path = "Weather_Planning_Agent_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path}")

if __name__ == "__main__":
    create_deck()
