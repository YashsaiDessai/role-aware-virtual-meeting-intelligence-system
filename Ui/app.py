"""
🧠 Meeting Intelligence — Landing Page

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
    page_title="🧠 Meeting Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ===================================================================== #
#  THREE.JS HERO SCENE
# ===================================================================== #
SCENE_HTML = (Path(__file__).parent / "home_scene.html").read_text(encoding="utf-8")
components.html(SCENE_HTML, height=600, scrolling=False)

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
    [data-testid="stSidebarNav"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }

    .block-container {
        padding-top: 0 !important;
        max-width: 1000px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }

    /* Make every Streamlit element wrapper full-width and centered */
    [data-testid="stVerticalBlock"] {
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }

    [data-testid="element-container"] {
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
    }

    /* ── Three.js iframe ───────────────────────────────────────────── */
    iframe[title="streamlit_components_v1.html"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 0 !important;
        pointer-events: none !important;
        border: none !important;
    }

    [data-testid="stHtml"],
    [data-testid="element-container"]:has(iframe) {
        position: fixed !important;
        top: 0 !important; left: 0 !important;
        width: 100vw !important; height: 100vh !important;
        z-index: 0 !important;
        overflow: visible !important;
        pointer-events: none !important;
    }

    .block-container, [data-testid="stVerticalBlock"] {
        position: relative !important;
        z-index: 1 !important;
    }

    /* Collapse the component placeholder so it doesn't eat vertical space */
    [data-testid="stHtml"] {
        height: 0 !important;
        min-height: 0 !important;
        overflow: visible !important;
    }
    [data-testid="element-container"]:has(iframe) + [data-testid="element-container"],
    [data-testid="stVerticalBlock"] > [data-testid="element-container"]:first-child {
        margin: 0 !important;
        padding: 0 !important;
        height: 0 !important;
        min-height: 0 !important;
        overflow: visible !important;
    }

    /* ── Hero section ──────────────────────────────────────────────── */
    .hero-spacer { height: 1vh; }

    .hero-eyebrow {
        text-align: center;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: var(--cyan);
        letter-spacing: 6px;
        text-transform: uppercase;
        margin-bottom: 1rem;
        opacity: 0.8;
    }

    .hero-title {
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 3rem;
        text-align: center;
        background: linear-gradient(135deg, var(--cyan), var(--magenta), var(--violet));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 5px;
        text-transform: uppercase;
        line-height: 1.15;
        margin-bottom: 0.3rem;
        animation: glowPulse 3s ease-in-out infinite;
    }
    @keyframes glowPulse {
        0%, 100% { filter: drop-shadow(0 0 20px rgba(0,240,255,0.3)); }
        50%      { filter: drop-shadow(0 0 40px rgba(0,240,255,0.6)); }
    }

    .hero-subtitle {
        text-align: center;
        font-size: 0.78rem;
        color: var(--muted);
        letter-spacing: 5px;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }

    .hero-desc {
        text-align: center;
        width: 100%;
        max-width: 580px;
        margin: 0 auto 2rem auto;
        font-size: 0.88rem;
        line-height: 1.8;
        color: rgba(224, 230, 240, 0.65);
    }
    .hero-desc strong {
        color: var(--cyan);
    }

    /* ── Feature pills ─────────────────────────────────────────────── */
    .feature-row {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.8rem;
        flex-wrap: wrap;
        max-width: 700px;
        margin: 0 auto 2.5rem auto;
    }
    .feature-pill {
        background: rgba(0, 240, 255, 0.04);
        border: 1px solid var(--border);
        border-radius: 50px;
        padding: 0.5rem 1.2rem;
        font-size: 0.7rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--text);
        backdrop-filter: blur(8px);
        transition: all 0.3s ease;
        white-space: nowrap;
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
        font-size: 0.9rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: #0a0a12 !important;
        background: linear-gradient(135deg, var(--cyan), var(--mint)) !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.9rem 2.8rem !important;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 0 25px rgba(0,240,255,0.25), 0 0 50px rgba(0,240,255,0.08);
    }
    .stButton > button:hover {
        box-shadow: 0 0 35px rgba(0,240,255,0.45), 0 0 70px rgba(0,255,179,0.2);
        transform: translateY(-2px);
    }

    /* ── Footer ────────────────────────────────────────────────────── */
    .home-footer {
        text-align: center;
        margin-top: 2.5rem;
        padding: 1rem;
        font-size: 0.6rem;
        color: rgba(107, 115, 148, 0.4);
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
#  3D SHOWCASE — Spacer that lets the neural sphere show through
# ===================================================================== #
st.markdown(
    '<div style="height:40vh; display:flex; align-items:flex-end; justify-content:center; padding-bottom:2rem;">'
    '<div style="text-align:center; animation:bounce 2s ease-in-out infinite;">'
    '<p style="font-family:JetBrains Mono,monospace; font-size:0.65rem; color:rgba(0,240,255,0.4); letter-spacing:4px; text-transform:uppercase; margin-bottom:0.3rem;">Scroll Down</p>'
    '<p style="font-size:1.2rem; color:rgba(0,240,255,0.4);">▼</p>'
    '</div>'
    '</div>'
    '<style>@keyframes bounce { 0%,100% { transform:translateY(0); } 50% { transform:translateY(8px); } }</style>',
    unsafe_allow_html=True,
)

# ===================================================================== #
#  HERO CONTENT — Single HTML block for perfect centering
# ===================================================================== #
st.markdown(
    '<div style="width:100%; display:flex; flex-direction:column; align-items:center; padding-top:3vh;">'\
    '<p style="text-align:center; width:100%; font-family:JetBrains Mono,monospace; font-size:0.7rem; color:#00f0ff; letter-spacing:6px; text-transform:uppercase; margin-bottom:1rem; opacity:0.8;">⬡ Local-First · Zero Data Leakage</p>'
    '<h1 style="text-align:center; width:100%; font-family:Orbitron,sans-serif; font-weight:900; font-size:3rem; background:linear-gradient(135deg,#00f0ff,#ff0099,#8b00ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; letter-spacing:5px; text-transform:uppercase; line-height:1.15; margin-bottom:0.3rem;">Meeting<br>Architect</h1>'
    '<p style="text-align:center; width:100%; font-size:0.78rem; color:#6b7394; letter-spacing:5px; text-transform:uppercase; margin-bottom:1.8rem;">Role-Aware Intelligence System</p>'
    '<div style="text-align:center; width:100%; max-width:560px; margin:0 auto 2rem auto; font-size:0.88rem; line-height:1.8; color:rgba(224,230,240,0.65);">'
    'Transform raw meeting transcripts into <strong style="color:#00f0ff;">structured intelligence</strong> '
    '— decisions, action items, and role-tailored summaries. '
    'Powered by <strong style="color:#00f0ff;">local LLM inference</strong> with complete privacy.'
    '</div>'
    '<div style="display:flex; justify-content:center; align-items:center; gap:0.8rem; flex-wrap:wrap; max-width:700px; margin:0 auto 2rem auto; width:100%;">'
    '<div class="feature-pill"><span class="pill-icon">🔒</span> Private</div>'
    '<div class="feature-pill"><span class="pill-icon">🧠</span> Local LLM</div>'
    '<div class="feature-pill"><span class="pill-icon">🎯</span> Role-Aware</div>'
    '<div class="feature-pill"><span class="pill-icon">⚡</span> JSON Output</div>'
    '<div class="feature-pill"><span class="pill-icon">🎙️</span> Voice-to-Text</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

# CTA Button — navigates to the Analyzer page
if st.button("🚀  LAUNCH ANALYZER"):
    st.switch_page("pages/1_Analyzer.py")

st.markdown(
    '<div style="text-align:center; margin-top:2rem; padding:1rem; font-size:0.6rem; color:rgba(107,115,148,0.4); letter-spacing:3px; text-transform:uppercase;">'
    'Built for Hackathons · Gemma 4 + Whisper · No Cloud Required'
    '</div>',
    unsafe_allow_html=True,
)
