# emotion_detection_app.py
# ─────────────────────────────────────────────────────────────────────────────
# Multi-Agent Emotion Detection from Voice
# Pattern: Supervisor → Researcher (Tavily) → Emotion Analyzer (Groq)
#
# Setup:
#   1. Copy .env.example to .env and fill in your keys
#   2. pip install -r requirements.txt
#   3. streamlit run emotion_detection_app.py
# ─────────────────────────────────────────────────────────────────────────────

import os
import re
import operator
import tempfile
import streamlit as st
from typing import Annotated, List, TypedDict, Literal
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from groq import Groq

# ── Load .env (looks in the same directory as this script) ───────────────────
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# Propagate into environment so LangChain/Groq SDKs pick them up
os.environ["GROQ_API_KEY"]   = GROQ_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Voice Emotion Detector",
    page_icon="🎙️",
    layout="centered",
)

st.title("🎙️ Voice Emotion Detector")
st.caption("Multi-agent AI: Supervisor · Researcher · Emotion Analyzer")

# ── Abort early with a clear message if keys are missing ─────────────────────
if not GROQ_API_KEY or not TAVILY_API_KEY:
    st.error(
        "**API keys not found.** "
        "Create a `.env` file in the same folder as this script with:\n\n"
        "```\n"
        "GROQ_API_KEY=gsk_...\n"
        "TAVILY_API_KEY=tvly-...\n"
        "```\n\n"
        "Then restart the app with `streamlit run emotion_detection_app.py`."
    )
    st.stop()

# ── Sidebar: info only (no key inputs) ───────────────────────────────────────
with st.sidebar:
    st.markdown("### How it works")
    st.markdown(
        "1. Upload or record audio\n"
        "2. Groq Whisper transcribes it\n"
        "3. Supervisor routes agents:\n"
        "   - 🔍 **Researcher** searches emotion cues via Tavily\n"
        "   - 🧠 **Analyzer** produces emotion report\n"
        "4. Results appear below"
    )
    st.markdown("---")
    st.markdown("**Model:** `llama-3.3-70b-versatile`")
    st.markdown("**Transcription:** `whisper-large-v3`")
    st.markdown("---")
    # Show masked key status so user knows keys loaded correctly
    def mask(k: str) -> str:
        return f"`{k[:8]}...{k[-4:]}`" if len(k) > 12 else "`(too short)`"
    st.markdown("**Keys loaded from `.env`**")
    st.markdown(f"Groq: {mask(GROQ_API_KEY)}")
    st.markdown(f"Tavily: {mask(TAVILY_API_KEY)}")

# ── Agent State ───────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    transcript:        str
    research_notes:    Annotated[List[str], operator.add]
    draft:             str
    next_node:         str
    retry_count:       int
    revision_feedback: str

# ── Supervisor routing schema ─────────────────────────────────────────────────
class Router(BaseModel):
    """Decide which worker to call next."""
    next_worker:  Literal["researcher", "analyzer", "FINISH"] = Field(
        description="The next node to act"
    )
    instructions: str = Field(description="Specific instructions for the worker")

# ── Build graph (cached — only rebuilt if keys change) ────────────────────────
@st.cache_resource
def build_graph(_groq_key: str, _tavily_key: str):
    os.environ["GROQ_API_KEY"]   = _groq_key
    os.environ["TAVILY_API_KEY"] = _tavily_key

    llm         = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)
    search_tool = TavilySearchResults(k=3)

    # ── Node: Researcher ───────────────────────────────────────────────────
    def researcher(state: AgentState):
        query   = f"emotion detection cues in speech: {state['transcript'][:300]}"
        results = search_tool.invoke(query)
        note    = (
            "[Research] Searched for emotion cues in transcript snippet.\n"
            f"Results:\n{results}"
        )
        return {"research_notes": [note], "retry_count": 0}

    # ── Node: Emotion Analyzer ─────────────────────────────────────────────
    def analyzer(state: AgentState):
        context = "\n".join(state["research_notes"])
        prompt  = f"""
You are an expert emotion analyst.

Transcript:
\"\"\"
{state['transcript']}
\"\"\"

Research context:
{context}

Analyse the transcript and produce a structured emotion report with:
1. **Primary emotion** detected (e.g. joy, sadness, anger, fear, surprise, disgust, neutral)
2. **Confidence** (High / Medium / Low) and why
3. **Secondary emotions** if present
4. **Key linguistic cues** that led to this analysis
5. **Tone summary** (1-2 sentences)

Be specific and grounded in the actual words of the transcript.
"""
        res = llm.invoke(prompt)
        return {"draft": res.content}

    # ── Node: Supervisor ───────────────────────────────────────────────────
    def supervisor(state: AgentState):
        structured_llm = llm.with_structured_output(Router)
        prompt = f"""
You are a supervisor orchestrating emotion analysis of a voice transcript.

Transcript (first 200 chars): {state['transcript'][:200]}
Research notes collected: {len(state['research_notes'])}
Current analysis draft length: {len(state['draft'])}

Rules:
- If research_notes is empty → route to "researcher"
- If research_notes exist but draft is empty → route to "analyzer"
- If draft exists and is substantial (>100 chars) → route to "FINISH"
"""
        decision = structured_llm.invoke(prompt)
        return {
            "next_node":         decision.next_worker,
            "revision_feedback": decision.instructions,
        }

    # ── Assemble graph ─────────────────────────────────────────────────────
    builder = StateGraph(AgentState)
    builder.add_node("supervisor", supervisor)
    builder.add_node("researcher", researcher)
    builder.add_node("analyzer",   analyzer)

    builder.set_entry_point("supervisor")
    builder.add_conditional_edges(
        "supervisor",
        lambda x: x["next_node"],
        {"researcher": "researcher", "analyzer": "analyzer", "FINISH": END},
    )
    builder.add_edge("researcher", "supervisor")
    builder.add_edge("analyzer",   "supervisor")

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


# ── Transcription helper ──────────────────────────────────────────────────────
def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    client = Groq(api_key=GROQ_API_KEY)
    suffix = os.path.splitext(filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        with open(tmp_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=(filename, f),
                response_format="text",
            )
        return transcription
    finally:
        os.unlink(tmp_path)


# ── Emotion colour map ────────────────────────────────────────────────────────
EMOTION_COLORS = {
    "joy":       "#22c55e",
    "happiness": "#22c55e",
    "sadness":   "#3b82f6",
    "anger":     "#ef4444",
    "fear":      "#a855f7",
    "surprise":  "#f59e0b",
    "disgust":   "#84cc16",
    "neutral":   "#6b7280",
}

def emotion_color(text: str) -> str:
    t = text.lower()
    for k, v in EMOTION_COLORS.items():
        if k in t:
            return v
    return "#6b7280"


# ── Main UI ───────────────────────────────────────────────────────────────────
st.markdown("### Step 1 — Provide audio")

input_mode = st.radio(
    "Input method",
    ["Upload audio file", "Paste / type transcript directly"],
    horizontal=True,
)

transcript = ""

if input_mode == "Upload audio file":
    uploaded = st.file_uploader(
        "Upload an audio file",
        type=["mp3", "wav", "m4a", "ogg", "webm", "mp4"],
        help="Supports mp3, wav, m4a, ogg, webm, mp4",
    )
    if uploaded:
        st.audio(uploaded)
        if st.button("📝 Transcribe with Groq Whisper"):
            with st.spinner("Transcribing with Whisper large-v3…"):
                try:
                    transcript = transcribe_audio(uploaded.read(), uploaded.name)
                    st.session_state["transcript"] = transcript
                    st.success("Transcription complete!")
                except Exception as e:
                    st.error(f"Transcription failed: {e}")

    if "transcript" in st.session_state:
        transcript = st.session_state["transcript"]

else:
    transcript = st.text_area(
        "Paste or type your transcript",
        placeholder="e.g. I can't believe they did that to me! I'm so frustrated…",
        height=120,
    )

if transcript:
    with st.expander("📄 Transcript", expanded=True):
        st.write(transcript)

st.markdown("---")
st.markdown("### Step 2 — Run emotion analysis")

if transcript and st.button("🚀 Analyse emotions", type="primary", use_container_width=True):

    graph = build_graph(GROQ_API_KEY, TAVILY_API_KEY)

    initial_state = {
        "transcript":        transcript,
        "research_notes":    [],
        "draft":             "",
        "next_node":         "",
        "retry_count":       0,
        "revision_feedback": "",
    }
    config = {"configurable": {"thread_id": "emotion_session_1"}}

    status_box  = st.empty()
    agent_steps = []

    with st.spinner("Multi-agent pipeline running…"):
        for event in graph.stream(initial_state, config, stream_mode="values"):
            node = event.get("next_node", "")
            if node and node not in agent_steps:
                agent_steps.append(node)
                icons = {
                    "researcher": "🔍 Researcher is searching Tavily…",
                    "analyzer":   "🧠 Emotion Analyzer is writing report…",
                    "FINISH":     "✅ Supervisor says: FINISH",
                }
                status_box.info(icons.get(node, f"⚙️ Routing to: {node}"))

        final = graph.get_state(config).values

    status_box.empty()

    # ── Results ────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🎯 Emotion Analysis Report")

    draft = final.get("draft", "")
    if draft:
        primary_match  = re.search(
            r"\*\*Primary emotion\*\*[:\s]+([A-Za-z]+)", draft, re.IGNORECASE
        )
        primary_emotion = primary_match.group(1) if primary_match else "Analysed"
        color           = emotion_color(primary_emotion)

        st.markdown(
            f'<div style="display:inline-block;background:{color}22;border:1.5px solid {color};'
            f'border-radius:8px;padding:4px 14px;margin-bottom:12px;">'
            f'<span style="color:{color};font-weight:600;font-size:1rem;">'
            f'{primary_emotion.capitalize()}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(draft)
    else:
        st.warning("No draft produced. The supervisor may have routed unexpectedly.")

    with st.expander("🔎 Agent execution trace"):
        st.code(" → ".join(["supervisor"] + agent_steps), language=None)
        notes = final.get("research_notes", [])
        if notes:
            st.markdown("**Research notes collected:**")
            for i, note in enumerate(notes, 1):
                st.markdown(f"*Note {i}:*")
                st.text(note[:800] + ("…" if len(note) > 800 else ""))

elif not transcript:
    st.info("Provide a transcript or upload audio above to continue.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "Built with LangGraph · Groq Llama 3.3 70B · Groq Whisper · Tavily Search · Streamlit"
)
