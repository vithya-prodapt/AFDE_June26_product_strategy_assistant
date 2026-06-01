import os
import sys
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Product Strategy Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header { font-size:2rem; font-weight:700; color:#1a237e; margin-bottom:0.2rem; }
    .sub-header  { color:#546e7a; font-size:1rem; margin-bottom:1rem; }
    .agent-card  { background:#f5f5f5; border-left:4px solid #1a237e;
                   padding:0.75rem 1rem; border-radius:6px; margin-bottom:0.5rem; }
    .metric-card { background:#e8eaf6; border-radius:8px; padding:1rem; text-align:center; }
    .swot-box    { border-radius:8px; padding:1rem; margin-bottom:0.5rem; }
    .strength-box    { background:#e8f5e9; border-left:4px solid #43a047; }
    .weakness-box    { background:#fff3e0; border-left:4px solid #fb8c00; }
    .opportunity-box { background:#e3f2fd; border-left:4px solid #1e88e5; }
    .threat-box      { background:#fce4ec; border-left:4px solid #e53935; }
</style>
""", unsafe_allow_html=True)


# ── Session state ───────────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "analysis_results": None,
        "chat_history": [],
        "vector_store": None,
        "agent_status": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _check_api_key() -> bool:
    key = os.getenv("OPENAI_API_KEY", "")
    if not key or key == "your_openai_api_key_here":
        st.error("⚠️ OPENAI_API_KEY is not set. Add it to a `.env` file or set it as an environment variable.")
        st.code("OPENAI_API_KEY=sk-...", language="bash")
        return False
    return True


# ── Sidebar ─────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=64)
        st.markdown("### AI Product Strategy Assistant")
        st.divider()

        st.markdown("**📁 Upload Business Data**")
        uploaded_files = st.file_uploader(
            "CSV, PDF, or TXT files",
            type=["csv", "pdf", "txt"],
            accept_multiple_files=True,
            help="Upload sales reports, customer reviews, market research, competitor info, etc.",
            label_visibility="collapsed",
        )

        if uploaded_files:
            for f in uploaded_files:
                st.markdown(f"<div class='agent-card'>📄 {f.name}</div>", unsafe_allow_html=True)

            if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
                if _check_api_key():
                    _run_analysis(uploaded_files)

        st.divider()

        if st.session_state.analysis_results:
            st.markdown("**📊 Export**")
            if st.button("Generate PDF Report", use_container_width=True):
                _download_pdf()

        st.divider()
        st.markdown("""
**Agents Active:**
- 👥 Customer Feedback Agent
- 📈 Sales Analysis Agent
- 🔍 Competitor Analysis Agent
- ⚖️ SWOT Analysis Agent
- 🎯 Feature Prioritization Agent
- 📋 Executive Report Agent
        """)


def _run_analysis(uploaded_files):
    from utils.data_processor import DataProcessor
    from utils.vector_store import VectorStore
    from agents.orchestrator import AgentOrchestrator

    st.session_state.agent_status = []
    status_placeholder = st.sidebar.empty()

    def progress_cb(msg: str):
        st.session_state.agent_status.append(msg)
        status_placeholder.info(msg)

    with st.spinner("Processing uploaded files..."):
        processor = DataProcessor()
        processed_data = processor.process_files(uploaded_files)

    with st.spinner("Building vector store..."):
        vs = VectorStore()
        vs.add_documents(processed_data)
        st.session_state.vector_store = vs

    with st.spinner("Running 6 AI Agents..."):
        orchestrator = AgentOrchestrator()
        try:
            results = orchestrator.run(processed_data, progress_callback=progress_cb)
            st.session_state.analysis_results = results
            status_placeholder.success("✅ Analysis complete!")
            st.rerun()
        except Exception as e:
            status_placeholder.error(f"Error: {e}")
            st.error(f"Analysis failed: {e}")


def _download_pdf():
    from utils.pdf_generator import PDFGenerator
    with st.spinner("Generating PDF..."):
        gen = PDFGenerator()
        pdf_bytes = gen.generate(st.session_state.analysis_results)
    st.sidebar.download_button(
        label="⬇️ Download PDF",
        data=pdf_bytes,
        file_name="product_strategy_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )


# ── SWOT renderer ────────────────────────────────────────────────────────────
def _render_swot(text: str):
    import re
    sections = {"Strengths": "", "Weaknesses": "", "Opportunities": "", "Threats": "", "Strategic Implications": ""}
    current = None
    for line in text.split("\n"):
        stripped = line.strip()
        matched = False
        for key in sections:
            if re.match(rf"^#{1,3}\s+{key}", stripped, re.IGNORECASE):
                current = key
                matched = True
                break
        if not matched and current:
            sections[current] += line + "\n"

    col1, col2 = st.columns(2)
    mapping = [
        ("Strengths", "strength-box", "💪 Strengths", col1),
        ("Weaknesses", "weakness-box", "⚠️ Weaknesses", col2),
        ("Opportunities", "opportunity-box", "🌟 Opportunities", col1),
        ("Threats", "threat-box", "🚧 Threats", col2),
    ]
    for key, css_class, label, col in mapping:
        content = sections.get(key, "").strip()
        if not content:
            continue
        with col:
            st.markdown(f"<div class='swot-box {css_class}'><b>{label}</b></div>", unsafe_allow_html=True)
            st.markdown(content)

    implications = sections.get("Strategic Implications", "").strip()
    if implications:
        st.markdown("### 🎯 Strategic Implications")
        st.markdown(implications)

    if not any(v.strip() for v in sections.values()):
        st.markdown(text)


# ── Chat handler ─────────────────────────────────────────────────────────────
def _handle_chat(question: str, results: dict, vector_store) -> str:
    import openai as _openai

    client = _openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL", "https://keygateway.arshnivlabs.com"),
    )

    rag_context = ""
    if vector_store:
        docs = vector_store.query(question, n_results=4)
        rag_context = "\n".join(docs)

    analysis_ctx = "\n\n".join(
        f"**{k.replace('_', ' ').title()}:**\n{v}"
        for k, v in results.items()
        if isinstance(v, str) and len(v) > 50
    )

    system = """You are an expert AI Product Strategy Assistant. Answer questions based on the
analysis results and document context provided. Be specific, cite data where available,
and keep answers concise and strategic."""

    msg = f"""Question: {question}

Analysis Results (summary):
{analysis_ctx[:4000]}

Relevant Document Context:
{rag_context[:1500]}

Provide a concise, data-driven strategic answer."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": msg},
        ],
    )
    return response.choices[0].message.content


# ── Welcome screen ───────────────────────────────────────────────────────────
def render_welcome():
    st.markdown("<div class='main-header'>🧠 AI Product Strategy Assistant</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Transform business data into actionable strategic insights</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Step 1: Upload Data**\n\nCSV sales reports, customer reviews, market research documents, competitor info")
    with col2:
        st.info("**Step 2: Run Analysis**\n\n6 specialized AI agents analyze different dimensions of your data")
    with col3:
        st.info("**Step 3: Get Insights**\n\nExplore reports, SWOT analysis, feature priorities, and download PDF")

    st.markdown("---")
    st.markdown("### 🤖 Multi-Agent Architecture")
    agents = [
        ("👥", "Customer Feedback Agent", "Sentiment analysis, pain points, satisfaction patterns"),
        ("📈", "Sales Analysis Agent", "Revenue trends, product performance, regional analysis"),
        ("🔍", "Competitor Analysis Agent", "Market positioning, competitive gaps, opportunities"),
        ("⚖️", "SWOT Analysis Agent", "Synthesizes all agents into comprehensive SWOT"),
        ("🎯", "Feature Prioritization Agent", "RICE/MoSCoW prioritization, roadmap suggestions"),
        ("📋", "Executive Report Agent", "Board-ready summary with 30-60-90 day action plan"),
    ]
    cols = st.columns(2)
    for i, (icon, name, desc) in enumerate(agents):
        with cols[i % 2]:
            st.markdown(f"<div class='agent-card'><b>{icon} {name}</b><br><small>{desc}</small></div>", unsafe_allow_html=True)


# ── Results tabs ─────────────────────────────────────────────────────────────
def render_results(results: dict):
    st.markdown("<div class='main-header'>🧠 AI Product Strategy Assistant</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Analysis complete — explore insights below</div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📋 Executive Report",
        "👥 Customer Insights",
        "📈 Sales Analysis",
        "🔍 Competitor Analysis",
        "⚖️ SWOT Analysis",
        "🎯 Feature Priorities",
        "💬 Chat",
    ])

    with tab1:
        st.header("Executive Summary")
        st.markdown(results.get("executive_report", "No data"))

    with tab2:
        st.header("Customer Insights Report")
        st.markdown(results.get("customer_feedback", "No data"))

    with tab3:
        st.header("Sales Analysis")
        st.markdown(results.get("sales_analysis", "No data"))

    with tab4:
        st.header("Competitor & Market Analysis")
        st.markdown(results.get("competitor_analysis", "No data"))

    with tab5:
        st.header("SWOT Analysis")
        _render_swot(results.get("swot_analysis", "No data"))

    with tab6:
        st.header("Feature Prioritization Recommendations")
        st.markdown(results.get("feature_prioritization", "No data"))

    with tab7:
        st.header("💬 Ask the Strategy Assistant")
        st.caption("Ask strategic questions about your data — the assistant uses all analysis results as context.")

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("e.g. Which product should we prioritize next quarter?"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    reply = _handle_chat(prompt, results, st.session_state.vector_store)
                st.markdown(reply)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    _init_state()
    render_sidebar()

    if st.session_state.analysis_results:
        render_results(st.session_state.analysis_results)
    else:
        render_welcome()


if __name__ == "__main__":
    main()
