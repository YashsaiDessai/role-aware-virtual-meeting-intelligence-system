"""
⚡ Analyzer — Transcript Processing Page

Cyberpunk-themed interface for inputting transcripts and viewing
role-aware analysis results from the MeetingAnalyzer engine.
The 3D background responds to the role selectbox — pulling the
active document plane to the front of the stack.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ── Ensure project root is importable ────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine import MeetingAnalyzer  # noqa: E402


# ── Cached analyzer (survives reruns) ────────────────────────────────
@st.cache_resource
def get_analyzer() -> MeetingAnalyzer:
    """Instantiate once — keeps model warm between interactions."""
    return MeetingAnalyzer()


# ===================================================================== #
#  PAGE CONFIG
# ===================================================================== #
st.set_page_config(
    page_title="⚡ Analyzer | Private Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ===================================================================== #
#  CYBERPUNK CSS + THREE.JS INJECTED DIRECTLY INTO THE PAGE DOM
# ===================================================================== #

# Read the Three.js scene template
BG_TEMPLATE = (Path(__file__).resolve().parent.parent / "background.html").read_text(
    encoding="utf-8"
)

# We need the role BEFORE injecting the 3D scene, so we use session state
# to remember the role across reruns while still injecting CSS first.
if "analyzer_role" not in st.session_state:
    st.session_state.analyzer_role = "Engineering"

# Extract just the <script> content from background.html for direct injection
# We'll load Three.js via CDN and run the scene script directly in the page
THREEJS_SCENE_SCRIPT = BG_TEMPLATE.replace("__ACTIVE_ROLE__", st.session_state.analyzer_role)

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=JetBrains+Mono:wght@300;400;500&display=swap');

    :root {{
      --cyan:    #00f0ff;
      --magenta: #ff0099;
      --violet:  #8b00ff;
      --mint:    #00ffb3;
      --bg:      #0a0a12;
      --card:    rgba(10, 10, 18, 0.75);
      --border:  rgba(0, 240, 255, 0.15);
      --text:    #e0e6f0;
      --muted:   #6b7394;
    }}

    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stApp"] {{
        background: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'JetBrains Mono', monospace !important;
    }}

    header[data-testid="stHeader"] {{ background: transparent !important; }}
    [data-testid="stAppViewBlockContainer"] {{ background: transparent !important; }}
    #MainMenu, footer, [data-testid="stDecoration"] {{ display: none !important; }}
    [data-testid="stSidebarNav"] {{ display: none !important; }}
    section[data-testid="stSidebar"] {{ display: none !important; }}

    .block-container {{
        padding-top: 1.5rem !important;
        max-width: 900px !important;
    }}

    /* ── Force the component iframe to render fullscreen behind content ── */
    iframe[title="streamlit_components_v1.html"] {{
        position: fixed !important;
        top: 0 !important; left: 0 !important;
        width: 100vw !important; height: 100vh !important;
        z-index: 0 !important;
        pointer-events: none !important;
        border: none !important;
    }}

    /* Ensure the iframe's PARENT container doesn't clip it */
    [data-testid="stHtml"],
    [data-testid="element-container"]:has(iframe) {{
        position: fixed !important;
        top: 0 !important; left: 0 !important;
        width: 100vw !important; height: 100vh !important;
        z-index: 0 !important;
        overflow: visible !important;
        pointer-events: none !important;
    }}

    /* Everything else sits above the 3D scene */
    .block-container, [data-testid="stVerticalBlock"] {{
        position: relative !important;
        z-index: 1 !important;
    }}

    h1 {{
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        font-size: 1.8rem !important;
        background: linear-gradient(135deg, var(--cyan), var(--magenta), var(--violet));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 3px;
        text-transform: uppercase;
        padding-bottom: 0.2rem;
    }}

    .page-sub {{
        font-size: 0.75rem;
        color: var(--muted);
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-bottom: 1.8rem;
    }}

    .glass-card {{
        background: var(--card);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 0 30px rgba(0,240,255,0.06), inset 0 0 60px rgba(0,240,255,0.02);
    }}

    .stSelectbox label, .stTextArea label, label {{
        font-family: 'Orbitron', sans-serif !important;
        font-size: 0.7rem !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        color: var(--cyan) !important;
    }}

    [data-testid="stSelectbox"] > div > div,
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    [data-testid="stSelectbox"] [data-baseweb="select"],
    [data-testid="stSelectbox"] input {{
        background: rgba(0, 240, 255, 0.05) !important;
        background-color: rgba(0, 240, 255, 0.05) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text) !important;
    }}
    [data-baseweb="popover"], [data-baseweb="popover"] ul,
    [data-baseweb="menu"], [role="listbox"] {{
        background: #0d0d1a !important;
        background-color: #0d0d1a !important;
        border: 1px solid var(--border) !important;
    }}
    [data-baseweb="menu"] li, [role="option"] {{ color: var(--text) !important; }}
    [data-baseweb="menu"] li:hover, [role="option"]:hover {{
        background: rgba(0, 240, 255, 0.1) !important;
    }}

    .stTextArea textarea, .stTextArea div,
    [data-testid="stTextArea"] textarea,
    [data-testid="stTextArea"] div[data-baseweb="textarea"],
    [data-testid="stTextArea"] div[data-baseweb="base-input"],
    [data-baseweb="textarea"], [data-baseweb="base-input"],
    textarea {{
        background: rgba(10, 10, 18, 0.9) !important;
        background-color: rgba(10, 10, 18, 0.9) !important;
        color: #e0e6f0 !important;
        caret-color: #00f0ff !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.82rem !important;
        line-height: 1.6 !important;
    }}
    .stTextArea textarea::placeholder, textarea::placeholder {{
        color: #4a5068 !important; opacity: 1 !important;
    }}
    .stTextArea textarea:focus, textarea:focus {{
        border-color: var(--cyan) !important;
        box-shadow: 0 0 15px rgba(0,240,255,0.2) !important;
        outline: none !important;
    }}
    input, select, [data-baseweb="input"] {{
        background: rgba(10, 10, 18, 0.9) !important;
        background-color: rgba(10, 10, 18, 0.9) !important;
        color: #e0e6f0 !important;
        border: 1px solid var(--border) !important;
    }}

    .stButton > button {{
        width: 100%;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700; font-size: 0.85rem;
        letter-spacing: 3px; text-transform: uppercase;
        color: #0a0a12 !important;
        background: linear-gradient(135deg, var(--cyan), var(--mint)) !important;
        border: none !important; border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        transition: all 0.3s ease;
        box-shadow: 0 0 20px rgba(0,240,255,0.25);
    }}
    .stButton > button:hover {{
        box-shadow: 0 0 35px rgba(0,240,255,0.5), 0 0 60px rgba(0,255,179,0.2);
        transform: translateY(-1px);
    }}

    [data-testid="stAlert"] {{
        background: rgba(0, 240, 255, 0.06) !important;
        border: 1px solid rgba(0, 240, 255, 0.2) !important;
        border-left: 4px solid var(--cyan) !important;
        border-radius: 8px !important;
        color: var(--text) !important; font-size: 0.88rem;
    }}

    h3 {{
        font-family: 'Orbitron', sans-serif !important;
        font-size: 0.9rem !important; letter-spacing: 2px !important;
        color: var(--cyan) !important;
        border-bottom: 1px solid var(--border);
        padding-bottom: 0.5rem; margin-top: 1.5rem !important;
    }}

    .stTable table, .stDataFrame table {{ width: 100%; border-collapse: separate; border-spacing: 0; }}
    .stTable thead th, .stDataFrame thead th {{
        background: rgba(0, 240, 255, 0.08) !important;
        color: var(--cyan) !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 0.65rem !important; letter-spacing: 2px !important;
        text-transform: uppercase !important;
        border-bottom: 1px solid var(--border) !important; padding: 0.7rem 1rem !important;
    }}
    .stTable tbody td, .stDataFrame tbody td {{
        background: rgba(10, 10, 18, 0.6) !important;
        color: var(--text) !important; font-size: 0.82rem !important;
        border-bottom: 1px solid rgba(0,240,255,0.06) !important; padding: 0.6rem 1rem !important;
    }}
    .stTable tbody tr:hover td {{ background: rgba(0, 240, 255, 0.05) !important; }}

    .decision-item {{
        padding: 0.6rem 1rem; margin-bottom: 0.4rem;
        background: rgba(139, 0, 255, 0.06);
        border-left: 3px solid var(--violet);
        border-radius: 0 6px 6px 0; font-size: 0.85rem;
    }}

    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: var(--bg); }}
    ::-webkit-scrollbar-thumb {{ background: rgba(0,240,255,0.2); border-radius: 3px; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ===================================================================== #
#  HEADER + BACK NAVIGATION
# ===================================================================== #
bcol1, bcol2 = st.columns([1, 8])
with bcol1:
    if st.button("← BACK"):
        st.switch_page("app.py")

st.title("⚡ Analyzer")
st.markdown(
    '<p class="page-sub">Paste transcript · Select role · Extract intelligence</p>',
    unsafe_allow_html=True,
)


# ===================================================================== #
#  INPUT SECTION
# ===================================================================== #
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    role = st.selectbox(
        "Stakeholder Lens",
        options=["Engineering", "Product", "Management"],
        index=["Engineering", "Product", "Management"].index(
            st.session_state.analyzer_role
        ),
        key="role_select",
    )
    # Update session state so the 3D scene uses the new role on next rerun
    if role != st.session_state.analyzer_role:
        st.session_state.analyzer_role = role
        st.rerun()

with col2:
    st.markdown(
        f"""
        <div style="padding:0.5rem 0; color: var(--muted); font-size:0.75rem; letter-spacing:1px;">
            {'🔧 Tech debt · Blockers · Architecture' if role == 'Engineering'
             else '📦 Roadmap · Features · Customer impact' if role == 'Product'
             else '📊 Risks · Deadlines · Resource allocation'}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ===================================================================== #
#  THREE.JS ROLE-AWARE BACKGROUND (rendered via components.html)
# ===================================================================== #
BG_HTML = BG_TEMPLATE.replace("__ACTIVE_ROLE__", st.session_state.analyzer_role)
components.html(BG_HTML, height=600, scrolling=False)


transcript = st.text_area(
    "Meeting Transcript",
    height=220,
    placeholder="Paste your raw meeting transcript here ...",
)

process = st.button("⚡  ANALYZE TRANSCRIPT", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)


# ===================================================================== #
#  PROCESSING & RESULTS
# ===================================================================== #
if process:
    if not transcript.strip():
        st.warning("⚠️  Paste a transcript above before analysing.")
    else:
        analyzer = get_analyzer()

        with st.spinner("🔮  Neural analysis in progress — querying local LLM ..."):
            try:
                result = analyzer.analyze(transcript, role)
            except RuntimeError as exc:
                st.error(f"❌  Inference failed: {exc}")
                st.stop()

        # ── Summary ──────────────────────────────────────────────────
        st.markdown("### 📋 Summary")
        st.info(result.summary)

        # ── Decisions ────────────────────────────────────────────────
        st.markdown("### 🎯 Key Decisions")
        if result.decisions:
            for d in result.decisions:
                st.markdown(
                    f'<div class="decision-item">{d}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No explicit decisions were identified.")

        # ── Action Items ─────────────────────────────────────────────
        st.markdown("### ⚡ Action Items")
        if result.action_items:
            rows = []
            for item in result.action_items:
                rows.append(
                    {
                        "Task": item.task,
                        "Owner": item.owner,
                        "Priority": item.priority.value.upper(),
                    }
                )
            df = pd.DataFrame(rows)
            st.table(df)
        else:
            st.caption("No action items were extracted.")
