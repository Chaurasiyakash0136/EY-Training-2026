"""
app.py — Streamlit UI for the Planner → Executor → Verifier multi-agent system
"""

import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()
import time
from agents import get_llm
from graph  import build_graph, initial_state

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Multi-Agent Planner",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0f0c29, #302b63, #24243e);
    color: #e2e8f0;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p { color: #cbd5e1 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #f8fafc !important; }

/* ── Header banner ── */
.hero-banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f64f59 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    color: white;
    box-shadow: 0 8px 32px rgba(102,126,234,0.35);
}
.hero-banner h1 { font-size: 2rem; font-weight: 700; margin: 0 0 .3rem; }
.hero-banner p  { font-size: 1rem; opacity: .85; margin: 0; }

/* ── Agent cards ── */
.agent-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    margin-bottom: .75rem;
    box-shadow: 0 2px 8px rgba(0,0,0,.05);
    transition: box-shadow .2s;
}
.agent-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.10); }

/* ── Status pills ── */
.pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: .75rem;
    font-weight: 600;
    letter-spacing: .03em;
}
.pill-waiting  { background: #f1f5f9; color: #64748b; }
.pill-running  { background: #fef3c7; color: #92400e; }
.pill-done     { background: #dcfce7; color: #166534; }
.pill-failed   { background: #fee2e2; color: #991b1b; }

/* ── Score bar container ── */
.score-row {
    display: flex;
    align-items: center;
    gap: .75rem;
    margin: .35rem 0;
    font-size: .875rem;
}
.score-label { min-width: 130px; color: #475569; font-weight: 500; }
.score-bar-bg {
    flex: 1; height: 10px;
    background: #e2e8f0;
    border-radius: 999px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, #667eea, #764ba2);
    transition: width .6s ease;
}
.score-val { min-width: 38px; text-align: right; font-weight: 600; color: #1e293b; }

/* ── Result boxes ── */
.result-box {
    background: #f8fafc;
    border-left: 4px solid #667eea;
    border-radius: 0 8px 8px 0;
    padding: .85rem 1rem;
    margin: .5rem 0;
    font-size: .875rem;
    color: #1e293b;
    line-height: 1.6;
    font-family: 'Inter', sans-serif;
}

/* ── Task chip ── */
.task-chip {
    display: inline-flex;
    align-items: center;
    gap: .4rem;
    background: #ede9fe;
    color: #4c1d95;
    border-radius: 8px;
    padding: .35rem .75rem;
    font-size: .8rem;
    font-weight: 500;
    margin: .25rem .15rem;
}

/* ── Log area ── */
.log-box {
    background: #0f172a;
    color: #94a3b8;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: .78rem;
    line-height: 1.7;
    max-height: 260px;
    overflow-y: auto;
}

/* ── Metric cards ── */
.metric-card {
    background: linear-gradient(135deg, #667eea22, #764ba222);
    border: 1px solid #667eea44;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.metric-card .num { font-size: 1.8rem; font-weight: 700; color: #4c1d95; }
.metric-card .lbl { font-size: .8rem; color: #6b7280; margin-top: .15rem; }

/* ── Approve badge ── */
.approved-badge {
    background: linear-gradient(135deg, #22c55e, #16a34a);
    color: white;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    font-weight: 700;
    font-size: 1.1rem;
    text-align: center;
    box-shadow: 0 4px 16px rgba(34,197,94,.3);
}
.rejected-badge {
    background: linear-gradient(135deg, #ef4444, #dc2626);
    color: white;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    font-weight: 700;
    font-size: 1.1rem;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    api_key = st.text_input(
        "🔑 Groq API Key",
        type="password",
        value=os.getenv("GROQ_API_KEY", ""),
        placeholder="gsk_...",
        help="Get yours free at console.groq.com",
    )

    st.markdown("---")
    st.markdown("### 🏗️ Architecture")

    for step, color, desc in [
        ("1. Planner",  "#667eea", "Breaks goal into ≤5 tasks"),
        ("2. Executor", "#764ba2", "Runs tasks + optional web search"),
        ("3. Verifier", "#f64f59", "Scores & approves / retries"),
    ]:
        st.markdown(
            f'<div style="border-left:3px solid {color};padding:.4rem .75rem;'
            f'margin:.4rem 0;border-radius:0 6px 6px 0;background:{color}15;">'
            f'<b style="color:{color}">{step}</b><br>'
            f'<span style="font-size:.8rem;color:#94a3b8">{desc}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 📖 How it works")
    st.markdown(
        "- Max **3 retry loops** before force-approve\n"
        "- Verifier scores: **Completeness** (0.4) + **Accuracy** (0.3) + **Clarity** (0.3)\n"
        "- 🌐 DuckDuckGo web search per task\n"
        "- Powered by **Llama 3.1-8b** via Groq"
    )

    st.markdown("---")
    st.caption("Built with LangGraph + Streamlit")

# ── Hero ──────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-banner">
  <h1>🤖 Multi-Agent Pipeline</h1>
  <p>Planner → Executor → Verifier · Powered by LangGraph &amp; Groq (Llama 3.1)</p>
</div>
""", unsafe_allow_html=True)

# ── Goal input ────────────────────────────────────────────────────────────────

col_input, col_btn = st.columns([5, 1])
with col_input:
    goal = st.text_area(
        "🎯 Enter your goal",
        placeholder="e.g. Research and summarise the top 3 trends in renewable energy for 2025",
        height=90,
        label_visibility="visible",
    )
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("▶ Run", use_container_width=True, type="primary")

# ── Example goals ─────────────────────────────────────────────────────────────

with st.expander("💡 Example goals"):
    examples = [
        "Research and summarise the top 3 trends in agriculture for 2025",
        "Create a beginner study plan for learning Python in 30 days",
        "Summarise the key differences between RAG and fine-tuning for LLMs",
        "Analyse the pros and cons of electric vehicles for Indian consumers",
    ]
    cols = st.columns(2)
    for i, ex in enumerate(examples):
        if cols[i % 2].button(ex, key=f"ex_{i}", use_container_width=True):
            st.session_state["preset_goal"] = ex
            st.rerun()

# ── Pre-fill from example click ───────────────────────────────────────────────
if "preset_goal" in st.session_state:
    goal = st.session_state.pop("preset_goal")

# ── Run pipeline ──────────────────────────────────────────────────────────────

if run_btn:
    if not api_key:
        st.error("⛔ Please enter your Groq API key in the sidebar.")
        st.stop()
    if not goal.strip():
        st.warning("⚠️ Please enter a goal before running.")
        st.stop()

    st.markdown("---")
    st.markdown("## 🔄 Pipeline Execution")

    # ── Live log ──────────────────────────────────────────────────────────────
    log_lines: list[str] = []
    log_placeholder = st.empty()

    def log(msg: str):
        ts = time.strftime("%H:%M:%S")
        log_lines.append(f"[{ts}] {msg}")
        log_placeholder.markdown(
            '<div class="log-box">' +
            "<br>".join(log_lines[-20:]) +
            "</div>",
            unsafe_allow_html=True,
        )

    # ── Agent status row ──────────────────────────────────────────────────────
    st.markdown("### 🟢 Agent Status")
    s1, s2, s3 = st.columns(3)

    def status_card(col, emoji, title, status="waiting"):
        pills = {"waiting": "pill-waiting ⏳", "running": "pill-running ⚡", "done": "pill-done ✅", "retry": "pill-failed 🔁"}
        pill_cls, pill_icon = pills.get(status, pills["waiting"]).split(" ", 1)
        col.markdown(
            f'<div class="agent-card">'
            f'{emoji} <b>{title}</b><br>'
            f'<span class="pill {pill_cls}">{pill_icon} {status.title()}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Initial render
    status_card(s1, "📋", "Planner",  "waiting")
    status_card(s2, "⚡", "Executor", "waiting")
    status_card(s3, "✅", "Verifier", "waiting")

    # placeholders for live result panels
    planner_ph  = st.empty()
    executor_ph = st.empty()
    verifier_ph = st.empty()
    final_ph    = st.empty()

    # ── Execute ───────────────────────────────────────────────────────────────
    try:
        llm   = get_llm(api_key)
        state = initial_state(goal.strip())

        # --- Planner ---
        status_card(s1, "📋", "Planner", "running")
        log("🚀 **Planner** started …")
        from agents import planner as run_planner
        state = run_planner(state, llm, log)
        status_card(s1, "📋", "Planner", "done")

        # Show tasks
        chips = "".join(
            f'<span class="task-chip">📌 {t[:70]}{"…" if len(t)>70 else ""}</span>'
            for t in state["tasks"]
        )
        planner_ph.markdown(
            f'<div class="agent-card"><b>📋 Planner Output</b><br><br>{chips}</div>',
            unsafe_allow_html=True,
        )

        iteration = 0
        final_state = state

        while True:
            iteration += 1
            # --- Executor ---
            status_card(s2, "⚡", "Executor", "running")
            log(f"⚡ **Executor** iteration {iteration} …")
            from agents import executor as run_executor
            state = run_executor(state, llm, log)
            status_card(s2, "⚡", "Executor", "done")

            results_html = "".join(
                f'<div class="result-box"><b>Task {i+1}:</b> {t}<hr style="border:none;border-top:1px solid #e2e8f0;margin:.4rem 0">{r}</div>'
                for i, (t, r) in enumerate(zip(state["tasks"], state["results"]))
            )
            executor_ph.markdown(
                f'<div class="agent-card"><b>⚡ Executor Results — Iteration {iteration}</b><br><br>{results_html}</div>',
                unsafe_allow_html=True,
            )

            # --- Verifier ---
            status_card(s3, "✅", "Verifier", "running")
            log("🔍 **Verifier** evaluating …")
            from agents import verifier as run_verifier
            state = run_verifier(state, llm, log)
            final_state = state

            sc = state.get("scores", {})
            total         = sc.get("total", 0)
            completeness  = sc.get("completeness", 0)
            accuracy      = sc.get("accuracy", 0)
            clarity       = sc.get("clarity", 0)

            def bar(label, val, max_val):
                pct = min(int((val / max_val) * 100), 100) if max_val else 0
                return (
                    f'<div class="score-row">'
                    f'<span class="score-label">{label}</span>'
                    f'<div class="score-bar-bg"><div class="score-bar-fill" style="width:{pct}%"></div></div>'
                    f'<span class="score-val">{val:.2f}</span>'
                    f'</div>'
                )

            verdict_html = (
                f'<div style="margin-bottom:.5rem">'
                f'<b>Total score: </b><span style="font-size:1.2rem;font-weight:700;color:#4c1d95">{total:.2f}</span>'
                f'</div>'
                + bar("Completeness", completeness, 0.4)
                + bar("Accuracy",     accuracy,     0.3)
                + bar("Clarity",      clarity,      0.3)
            )
            if state.get("critique"):
                verdict_html += f'<br><b>Critique:</b> <i style="color:#64748b">{state["critique"]}</i>'

            status_card(s3, "✅", "Verifier", "done" if state["approved"] else "retry")
            verifier_ph.markdown(
                f'<div class="agent-card"><b>✅ Verifier — Iteration {iteration}</b><br><br>{verdict_html}</div>',
                unsafe_allow_html=True,
            )

            if state["approved"]:
                log(f"🎉 **Approved** after {iteration} iteration(s)!")
                break
            if state["iterations"] >= 3:
                log("⚠️ Max iterations reached.")
                break
            log(f"🔁 Retry loop {iteration + 1} …")

        # ── Final summary ─────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("## 🏁 Final Summary")

        m1, m2, m3, m4 = st.columns(4)
        for col, num, lbl in [
            (m1, len(final_state["tasks"]),  "Tasks planned"),
            (m2, final_state["iterations"],  "Iterations"),
            (m3, f"{final_state['scores'].get('total', 0):.2f}", "Quality score"),
            (m4, "✅ Yes" if final_state["approved"] else "❌ No", "Approved"),
        ]:
            col.markdown(
                f'<div class="metric-card"><div class="num">{num}</div>'
                f'<div class="lbl">{lbl}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        badge_cls = "approved-badge" if final_state["approved"] else "rejected-badge"
        badge_txt = "🎉 Pipeline completed successfully — results approved!" if final_state["approved"] else "⚠️ Pipeline completed — max iterations reached."
        final_ph.markdown(f'<div class="{badge_cls}">{badge_txt}</div>', unsafe_allow_html=True)

        # Download results
        st.markdown("### 📥 Download Results")
        report = f"# Multi-Agent Pipeline Report\n\n**Goal:** {goal}\n\n## Tasks\n"
        for i, t in enumerate(final_state["tasks"], 1):
            report += f"{i}. {t}\n"
        report += "\n## Results\n"
        for i, (t, r) in enumerate(zip(final_state["tasks"], final_state["results"]), 1):
            report += f"\n### Task {i}: {t}\n{r}\n"
        sc = final_state.get("scores", {})
        report += (
            f"\n## Verifier Scores\n"
            f"- Total: {sc.get('total', 0):.2f}\n"
            f"- Completeness: {sc.get('completeness', 0):.2f} / 0.40\n"
            f"- Accuracy: {sc.get('accuracy', 0):.2f} / 0.30\n"
            f"- Clarity: {sc.get('clarity', 0):.2f} / 0.30\n"
            f"- Approved: {final_state['approved']}\n"
            f"- Iterations: {final_state['iterations']}\n"
        )
        st.download_button(
            "⬇️ Download Report (.md)",
            data=report,
            file_name="pipeline_report.md",
            mime="text/markdown",
        )

    except Exception as e:
        st.error(f"❌ Pipeline error: {e}")
        st.exception(e)
