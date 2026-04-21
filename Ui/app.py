"""
🧠 Private Intelligence — Landing Page

Hero page with a Three.js neural sphere and navigation to the Analyzer.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# ===================================================================== #
#  PAGE CONFIG
# ===================================================================== #
st.set_page_config(
    page_title="🧠 Private Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ===================================================================== #
#  THREE.JS HERO SCENE
# ===================================================================== #
SCENE_HTML = (Path(__file__).parent / "home_scene.html").read_text(encoding="utf-8")
components.html(SCENE_HTML, height=0, scrolling=False)

# ===================================================================== #
#  CSS — CYBERPUNK LANDING PAGE
# ===================================================================== #
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=JetBrains+Mono:wght@300;400;500&display=swap');

    :root {
      --cyan:    #00f0ff;
      --magenta: #ff0099;
      --violet:  #8b00ff;
      --mint:    #00ffb3;
      --bg:      #0a0a12;
      --text:    #e0e6f0;
      --muted:   #6b7394;
      --border:  rgba(0, 240, 255, 0.15);
    }

    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stApp"] {
        background: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    header[data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stAppViewBlockContainer"] { background: transparent !important; }
    #MainMenu, footer, [data-testid="stDecoration"] { display: none !important; }

    /* Hide default Streamlit sidebar nav */
    [data-testid="stSidebarNav"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }

    .block-container {
        padding-top: 0 !important;
        max-width: 1000px !important;
    }

    /* ── Three.js iframe ───────────────────────────────────────────── */
    iframe {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: -1 !important;
        pointer-events: none !important;
        border: none !important;
    }

    /* ── Hero section ──────────────────────────────────────────────── */
    .hero-spacer { height: 18vh; }

    .hero-title {
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 3.2rem;
        text-align: center;
        background: linear-gradient(135deg, var(--cyan), var(--magenta), var(--violet));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 6px;
        text-transform: uppercase;
        line-height: 1.2;
        margin-bottom: 0.5rem;
        animation: glowPulse 3s ease-in-out infinite;
    }
    @keyframes glowPulse {
        0%, 100% { filter: drop-shadow(0 0 20px rgba(0,240,255,0.3)); }
        50%      { filter: drop-shadow(0 0 40px rgba(0,240,255,0.6)); }
    }

    .hero-subtitle {
        text-align: center;
        font-size: 0.9rem;
        color: var(--muted);
        letter-spacing: 5px;
        text-transform: uppercase;
        margin-bottom: 2.5rem;
    }

    .hero-desc {
        text-align: center;
        max-width: 620px;
        margin: 0 auto 3rem auto;
        font-size: 0.95rem;
        line-height: 1.8;
        color: rgba(224, 230, 240, 0.7);
    }
    .hero-desc strong {
        color: var(--cyan);
    }

    /* ── Feature pills ─────────────────────────────────────────────── */
    .feature-row {
        display: flex;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
        margin-bottom: 3rem;
    }
    .feature-pill {
        background: rgba(0, 240, 255, 0.04);
        border: 1px solid var(--border);
        border-radius: 50px;
        padding: 0.6rem 1.4rem;
        font-size: 0.75rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--text);
        backdrop-filter: blur(8px);
        transition: all 0.3s ease;
    }
    .feature-pill:hover {
        border-color: var(--cyan);
        box-shadow: 0 0 15px rgba(0,240,255,0.15);
    }
    .pill-icon { margin-right: 0.4rem; }

    /* ── CTA Button ────────────────────────────────────────────────── */
    .stButton > button {
        display: block;
        margin: 0 auto;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700;
        font-size: 0.95rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: #0a0a12 !important;
        background: linear-gradient(135deg, var(--cyan), var(--mint)) !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 1rem 3rem !important;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 0 30px rgba(0,240,255,0.3), 0 0 60px rgba(0,240,255,0.1);
    }
    .stButton > button:hover {
        box-shadow: 0 0 40px rgba(0,240,255,0.5), 0 0 80px rgba(0,255,179,0.3);
        transform: translateY(-2px);
    }

    /* ── Footer ────────────────────────────────────────────────────── */
    .home-footer {
        text-align: center;
        margin-top: 4rem;
        padding: 1rem;
        font-size: 0.65rem;
        color: rgba(107, 115, 148, 0.5);
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    /* ── Scrollbar ─────────────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: rgba(0,240,255,0.2); border-radius: 3px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===================================================================== #
#  HERO CONTENT
# ===================================================================== #
st.markdown('<div class="hero-spacer"></div>', unsafe_allow_html=True)

st.markdown(
    '<h1 class="hero-title">Private<br>Intelligence</h1>',
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="hero-subtitle">Role-Aware Meeting Analysis System</p>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <p class="hero-desc">
        Transform raw meeting transcripts into <strong>structured intelligence</strong>
        — decisions, action items, and role-tailored summaries.
        Powered by <strong>local LLM inference</strong> with zero data leakage.
    </p>
    """,
    unsafe_allow_html=True,
)

# Feature pills
st.markdown(
    """
    <div class="feature-row">
        <div class="feature-pill"><span class="pill-icon">🔒</span> 100% Private</div>
        <div class="feature-pill"><span class="pill-icon">🧠</span> Local LLM</div>
        <div class="feature-pill"><span class="pill-icon">🎯</span> Role-Aware</div>
        <div class="feature-pill"><span class="pill-icon">⚡</span> JSON Output</div>
        <div class="feature-pill"><span class="pill-icon">🔧</span> Ollama + Gemma</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# CTA Button — navigates to the Analyzer page
if st.button("🚀  LAUNCH ANALYZER"):
    st.switch_page("pages/1_Analyzer.py")

st.markdown(
    '<div class="home-footer">Built for hackathons · Powered by Gemma 4 · No cloud required</div>',
    unsafe_allow_html=True,
)
