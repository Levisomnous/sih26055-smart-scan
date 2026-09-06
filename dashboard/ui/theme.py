from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap');
        :root { --paper:#0d1012; --surface:#151a1d; --surface-alt:#1c2225; --surface-strong:#20282c; --ink:#f1f0eb; --muted:#9ea4a5; --faint:#687174; --border:#2a3235; --accent:#e3262e; --success:#6e9b78; --warning:#c89a4b; }
        html, body, [class*="css"] { font-family:'DM Sans', sans-serif; color:var(--ink); background:var(--paper); }
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] main { background:var(--paper); color:var(--ink); }
        .block-container { max-width:1440px; padding:2.3rem 3.2rem 4rem; }
        [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p, [data-testid="stCaptionContainer"], [data-testid="stDataFrame"] { color:var(--ink) !important; }
        [data-testid="stAppViewContainer"] h1,
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] h3,
        [data-testid="stAppViewContainer"] h4,
        [data-testid="stAppViewContainer"] strong { color:var(--ink) !important; }
        [data-testid="stAppViewContainer"] h1 { font-weight:700 !important; }
        [data-testid="stAppViewContainer"] h2, [data-testid="stAppViewContainer"] h3 { font-weight:600 !important; }
        [data-testid="stCaptionContainer"] p, .section-note, .header-subtitle, .boundary-note { color:var(--muted) !important; }
        [data-testid="stHeader"] { background:rgba(13,16,18,0.78); border-bottom:1px solid var(--border); }
        [data-testid="stSidebarCollapsedControl"] { background:var(--surface); border:1px solid var(--border); border-radius:8px; opacity:1 !important; visibility:visible !important; }
        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="stSidebarCollapsedControl"] button:hover,
        [data-testid="stSidebarCollapsedControl"] button:focus,
        [data-testid="stSidebarCollapsedControl"] svg { color:var(--ink) !important; background:transparent !important; opacity:1 !important; }
        [data-testid="stSidebar"] { background:#11181c; border-right:1px solid var(--border); }
        [data-testid="stSidebar"] > div:first-child { padding-top:2rem; }
        [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color:var(--ink) !important; }
        [data-testid="stSidebar"] input, [data-testid="stSidebar"] select, [data-testid="stSidebar"] [data-baseweb="select"] { color:var(--ink) !important; background:var(--surface) !important; }
        [data-testid="stSidebar"] [role="radiogroup"] label { color:var(--ink) !important; }
        [role="radio"][aria-checked="true"] { color:var(--accent) !important; }
        h1, h2, h3 { letter-spacing:0; color:var(--ink) !important; }
        h1 { font-size:2.75rem !important; line-height:1.05 !important; margin:0 !important; }
        h2 { font-size:1.15rem !important; margin:0 !important; }
        [data-testid="stMetric"] { background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:1rem 1.15rem; }
        [data-testid="stMetricLabel"] p { font-family:'Space Mono',monospace; font-size:.64rem; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
        [data-testid="stMetricValue"] { font-size:1.7rem; font-weight:600; }
        .stButton > button, .stDownloadButton > button { border:1px solid var(--border); border-radius:8px; min-height:2.7rem; font-weight:600; color:var(--ink); background:var(--surface); }
        .stButton > button:hover, .stDownloadButton > button:hover { border-color:var(--border); background:var(--surface-alt); color:var(--ink); }
        .stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] { border-color:var(--accent); background:var(--accent); color:#fff; }
        .stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover { color:#fff; background:#cf252b; }
        [data-testid="stDataFrame"] { border:1px solid var(--border); border-radius:8px; overflow:hidden; background:var(--surface-alt); }
        [data-testid="stDataFrame"] > div { background:var(--surface-alt); }
        .eyebrow, .section-label, .mono-label { font-family:'Space Mono',monospace; font-size:.64rem; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
        .eyebrow { color:var(--accent); margin-bottom:.65rem; }
        .header-row { display:flex; justify-content:space-between; gap:2rem; align-items:flex-start; margin-bottom:2rem; }
        .header-subtitle { color:var(--muted) !important; margin-top:.65rem; font-size:1rem; }
        .status-mark { color:var(--muted); font-family:'Space Mono',monospace; font-size:.66rem; letter-spacing:.06em; text-transform:uppercase; text-align:right; padding-top:.25rem; }
        .status-mark span { color:var(--accent); font-size:1rem; vertical-align:-1px; }
        .section-head { display:flex; justify-content:space-between; align-items:baseline; border-bottom:1px solid var(--border); padding-bottom:.65rem; margin:1.8rem 0 .9rem; }
        .scan-pipeline { display:flex; flex-wrap:wrap; gap:.8rem; align-items:center; margin:1rem 0 1.2rem; }
        .scan-step { background:var(--surface-alt); border:1px solid var(--border); border-radius:999px; padding:.45rem .8rem; font-family:'Space Mono',monospace; font-size:.62rem; letter-spacing:.08em; text-transform:uppercase; color:var(--ink); }
        .scan-arrow { color:var(--muted); font-size:1.05rem; }
        .pipeline-block { background:var(--surface-alt); border:1px solid var(--border); border-radius:8px; padding:.8rem .9rem; margin-top:.75rem; }
        .pipeline-block strong { display:block; color:var(--ink); font-size:.72rem; letter-spacing:.09em; font-family:'Space Mono',monospace; text-transform:uppercase; }
        .pipeline-block span { display:block; color:var(--muted); margin-top:.35rem; font-size:.74rem; line-height:1.5; }
        .info-card { background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:1rem 1.05rem; min-height:100%; }
        .info-card .mono-label { display:block; margin-bottom:.55rem; }
        .info-card p { margin:0; color:var(--muted); line-height:1.55; }
        .section-note { color:var(--muted); font-size:.78rem; }
        .surface { background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:1.2rem; }
        .summary-grid { display:grid; grid-template-columns:1fr 1fr; gap:.9rem 1.2rem; margin-top:1.1rem; }
        .summary-item { border-bottom:1px solid var(--border); padding-bottom:.6rem; }
        .summary-value { font-size:1.05rem; font-weight:600; margin-top:.2rem; }
        .summary-note { color:var(--muted); line-height:1.5; font-size:.8rem; margin-top:1.2rem; }
        .decision-band { font-size:3.8rem; line-height:1; font-weight:700; margin:.3rem 0 1.3rem; }
        .decision-band em { color:var(--accent); font-style:normal; }
        .decision-copy { color:var(--muted); font-size:.82rem; line-height:1.5; }
        .final-title { font-size:3.2rem; line-height:1; font-weight:700; margin:.2rem 0 .7rem; }
        .flow { font-family:'Space Mono',monospace; color:var(--accent); font-size:.72rem; letter-spacing:.08em; margin-top:1rem; }
        .metric-value { font-size:1.8rem; font-weight:600; margin-top:.45rem; }
        .sidebar-controls-label { margin-top:1.3rem; }
        .synthetic-dot { color:var(--accent); }
        .phase-line { display:grid; grid-template-columns:1fr auto 1fr; gap:1rem; align-items:center; margin-top:.8rem; }
        .phase-block { background:var(--surface-alt); border:1px solid var(--border); border-radius:8px; padding:.85rem 1rem; }
        .phase-block strong { display:block; color:var(--ink); margin-top:.25rem; }
        .phase-shift { color:var(--accent); font-family:'Space Mono',monospace; font-size:.65rem; text-align:center; white-space:nowrap; }
        .findings-table th { font-family:'Space Mono',monospace; font-size:.63rem; text-transform:uppercase; color:var(--muted); text-align:left; padding:.45rem .55rem; }
        .findings-table td { border-top:1px solid var(--border); padding:.55rem .55rem; font-size:.82rem; color:var(--ink); }
        .findings-table td:last-child { color:var(--accent); font-weight:600; }
        .status-ready { color:var(--success); font-family:'Space Mono',monospace; font-size:.66rem; letter-spacing:.06em; text-transform:uppercase; }
        div[data-testid="stMarkdownContainer"] table { width:100%; border-collapse:collapse; background:var(--surface); border:1px solid var(--border); border-radius:8px; overflow:hidden; }
        div[data-testid="stMarkdownContainer"] th { background:var(--surface-alt); color:var(--muted); font-family:'Space Mono',monospace; font-size:.62rem; letter-spacing:.08em; text-transform:uppercase; padding:.7rem .8rem; border-bottom:1px solid var(--border); }
        div[data-testid="stMarkdownContainer"] td { border-bottom:1px solid var(--border); padding:.7rem .8rem; color:var(--ink); }
        div[data-testid="stMarkdownContainer"] tr:last-child td { border-bottom:none; }
        div[data-testid="stMarkdownContainer"] a { color:var(--accent); }
        @media (max-width:900px) { .block-container { padding:1.5rem 1.1rem 3rem; } .header-row { display:block; } .status-mark { text-align:left; margin-top:1rem; } h1 { font-size:2.1rem !important; } .final-title { font-size:2.5rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )
