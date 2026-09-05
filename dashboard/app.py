from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.demo_runner import DemoRunner
from evaluation.benchmark import default_scheduler_factories, run_benchmark
from evaluation.runner import run_scheduler_with_history
from simulator.environment import ScenarioConfig, SyntheticRFEnvironment
from simulator.receiver import SimulatedReceiver


SCENARIOS = ["changing", "persistent", "periodic", "bursty", "mixed"]
STRATEGIES = ["Sequential", "Random", "Adaptive", "Smart Adaptive"]
HELD_OUT_SCENARIOS = ["periodic", "bursty", "mixed"]
STRATEGY_COLORS = {
    "Sequential": "#d9d8d3",
    "Random": "#b3b8ae",
    "Adaptive": "#777771",
    "Smart Adaptive": "#d71920",
}


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap');
        :root { --paper:#f5f4f0; --surface:#fff; --muted-surface:#eceae5; --ink:#151515; --muted:#777771; --border:#d9d8d3; --accent:#d71920; --success:#4e7a5a; }
        html, body, [class*="css"] { font-family:'DM Sans', sans-serif; color:var(--ink); }
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] main { background:var(--paper); color:var(--ink); }
        [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p, [data-testid="stCaptionContainer"] { color:var(--ink) !important; }
        [data-testid="stAppViewContainer"] h1,
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] h3,
        [data-testid="stAppViewContainer"] h4,
        [data-testid="stAppViewContainer"] strong { color:var(--ink) !important; }
        [data-testid="stAppViewContainer"] h1 { font-weight:700 !important; }
        [data-testid="stAppViewContainer"] h2, [data-testid="stAppViewContainer"] h3 { font-weight:600 !important; }
        [data-testid="stCaptionContainer"] p, .section-note, .header-subtitle { color:var(--muted) !important; }
        [data-testid="stHeader"] { background:transparent; }
        [data-testid="stToolbar"] { visibility:hidden; }
        [data-testid="stSidebar"] { background:#eeece7; border-right:1px solid var(--border); }
        [data-testid="stSidebar"] > div:first-child { padding-top:2rem; }
        [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color:var(--ink) !important; }
        [data-testid="stSidebar"] input, [data-testid="stSidebar"] select { color:var(--ink) !important; background:var(--surface) !important; }
        [data-testid="stSidebar"] [role="radiogroup"] label { color:var(--ink) !important; }
        .block-container { max-width:1440px; padding:2.3rem 3.2rem 4rem; }
        h1, h2, h3 { letter-spacing:0; color:var(--ink) !important; }
        h1 { font-size:2.65rem !important; line-height:1.05 !important; margin:0 !important; }
        h2 { font-size:1.15rem !important; margin:0 !important; }
        [data-testid="stMetric"] { background:var(--surface); border:1px solid var(--border); border-radius:6px; padding:1rem 1.15rem; }
        [data-testid="stMetricLabel"] p { font-family:'Space Mono',monospace; font-size:.64rem; letter-spacing:.04em; text-transform:uppercase; color:var(--muted); }
        [data-testid="stMetricValue"] { font-size:1.65rem; font-weight:600; }
        .stButton > button { border:1px solid var(--border); border-radius:5px; min-height:2.5rem; font-weight:600; color:var(--ink); background:var(--surface); }
        .stButton > button[kind="primary"] { border-color:var(--accent); background:var(--accent); color:white; }
        .stButton > button:hover { border-color:var(--accent); color:var(--accent); }
        .stButton > button[kind="primary"]:hover { color:white; }
        [data-testid="stDataFrame"] { border:1px solid var(--border); border-radius:6px; overflow:hidden; }
        .eyebrow, .section-label, .mono-label { font-family:'Space Mono',monospace; font-size:.64rem; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
        .eyebrow { color:var(--accent); margin-bottom:.65rem; }
        .header-row { display:flex; justify-content:space-between; gap:2rem; align-items:flex-start; margin-bottom:2rem; }
        .header-subtitle { color:var(--muted) !important; margin-top:.65rem; font-size:1rem; }
        .status-mark { color:var(--success); font-family:'Space Mono',monospace; font-size:.66rem; letter-spacing:.06em; text-transform:uppercase; text-align:right; padding-top:.25rem; }
        .status-mark span { color:var(--accent); font-size:1rem; vertical-align:-1px; }
        .section-head { display:flex; justify-content:space-between; align-items:baseline; border-bottom:1px solid var(--border); padding-bottom:.65rem; margin:1.8rem 0 .9rem; }
        .section-note { color:var(--muted); font-size:.78rem; }
        .surface { background:var(--surface); border:1px solid var(--border); border-radius:6px; padding:1.2rem; }
        .summary-grid { display:grid; grid-template-columns:1fr 1fr; gap:.9rem 1.2rem; margin-top:1.1rem; }
        .summary-item { border-bottom:1px solid var(--border); padding-bottom:.6rem; }
        .summary-value { font-size:1.05rem; font-weight:600; margin-top:.2rem; }
        .summary-note { color:var(--muted); line-height:1.5; font-size:.8rem; margin-top:1.2rem; }
        .decision-band { font-size:3.8rem; line-height:1; font-weight:700; margin:.3rem 0 1.3rem; }
        .decision-band em { color:var(--accent); font-style:normal; }
        .decision-copy { color:var(--muted); font-size:.82rem; line-height:1.5; }
        .final-title { font-size:3.4rem; line-height:1; font-weight:700; margin:.2rem 0 .7rem; }
        .flow { font-family:'Space Mono',monospace; color:var(--accent); font-size:.72rem; letter-spacing:.08em; margin-top:1rem; }
        .metric-value { font-size:1.8rem; font-weight:600; margin-top:.45rem; }
        .sidebar-controls-label { margin-top:1.3rem; }
        .synthetic-dot { color:var(--accent); }
        .phase-line { display:grid; grid-template-columns:1fr auto 1fr; gap:1rem; align-items:center; margin-top:.8rem; }
        .phase-block { background:var(--surface-muted); border:1px solid var(--border); border-radius:5px; padding:.85rem 1rem; }
        .phase-block strong { display:block; color:var(--ink); margin-top:.25rem; }
        .phase-shift { color:var(--accent); font-family:'Space Mono',monospace; font-size:.65rem; text-align:center; white-space:nowrap; }
        .findings-table th { font-family:'Space Mono',monospace; font-size:.63rem; text-transform:uppercase; color:var(--muted); text-align:left; padding:.45rem .5rem; }
        .findings-table td { border-top:1px solid var(--border); padding:.55rem .5rem; font-size:.82rem; }
        .findings-table td:last-child { color:var(--accent); font-weight:600; }
        .boundary-note { color:var(--muted); font-size:.78rem; line-height:1.5; }
        .status-ready { color:var(--success); font-family:'Space Mono',monospace; font-size:.66rem; letter-spacing:.06em; text-transform:uppercase; }
        @media (max-width:900px) { .block-container { padding:1.5rem 1.1rem 3rem; } .header-row { display:block; } .status-mark { text-align:left; margin-top:1rem; } h1 { font-size:2.1rem !important; } .final-title { font-size:2.5rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def app_header(kicker: str) -> None:
    st.markdown(
        f"""
        <div class="header-row"><div><div class="eyebrow">SPECTRUM INTELLIGENCE // SIH26055</div>
        <h1>Smart Scan Strategy</h1><div class="header-subtitle">Adaptive decision-making in a synthetic RF environment</div></div>
        <div class="status-mark"><span>●</span> SYNTHETIC ONLY<br>ACADEMIC PROJECT<br><br>{kicker}</div></div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, note: str = "") -> None:
    st.markdown(f'<div class="section-head"><div class="section-label">{title}</div><div class="section-note">{note}</div></div>', unsafe_allow_html=True)


def metric_card(label: str, value: str, accent: bool = False) -> None:
    color = "#d71920" if accent else "#151515"
    st.markdown(f'<div class="surface"><div class="mono-label">{label}</div><div class="metric-value" style="color:{color}">{value}</div></div>', unsafe_allow_html=True)


def make_environment(scenario: str, bands: int, steps: int, seed: int) -> SyntheticRFEnvironment:
    return SyntheticRFEnvironment(ScenarioConfig(scenario, bands, steps, seed))


def load_held_out_findings() -> pd.DataFrame:
    path = PROJECT_ROOT / "data" / "multiseed_summary.csv"
    if not path.exists():
        return pd.DataFrame()

    summary = pd.read_csv(path)
    return summary[
        summary["scenario"].isin(HELD_OUT_SCENARIOS)
        & summary["metric"].eq("interception_ratio")
        & summary["strategy"].isin(["Adaptive", "Smart Adaptive"])
    ].copy()


def get_scan_histories(
    scenario: str,
    bands: int,
    steps: int,
    seed: int,
) -> dict[str, list]:
    """Run the existing strategies once to expose their actual scan histories."""

    histories: dict[str, list] = {}
    for name, create_scheduler in default_scheduler_factories(bands, seed).items():
        environment = make_environment(scenario, bands, steps, seed)
        _, history = run_scheduler_with_history(environment, create_scheduler())
        histories[name] = history
    return histories


def make_allocation_chart(
    histories: dict[str, list],
    bands: int,
) -> plt.Figure:
    counts = pd.DataFrame(0, index=range(1, bands + 1), columns=STRATEGIES)
    for strategy, history in histories.items():
        for record in history:
            counts.loc[record.band + 1, strategy] += 1

    fig, ax = plt.subplots(figsize=(9.5, 3.8), dpi=120)
    fig.patch.set_facecolor("#ffffff")
    counts.plot.bar(
        ax=ax,
        width=.82,
        color=[STRATEGY_COLORS[strategy] for strategy in STRATEGIES],
    )
    ax.set_xlabel("Frequency band", fontsize=8, color="#777771")
    ax.set_ylabel("Scan opportunities", fontsize=8, color="#777771")
    ax.tick_params(axis="x", labelsize=7, colors="#777771", rotation=0)
    ax.tick_params(axis="y", labelsize=8, colors="#777771")
    ax.grid(axis="y", color="#eceae5", linewidth=.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=7, ncol=4, loc="upper center", bbox_to_anchor=(.5, 1.13))
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout(pad=1.2)
    return fig


def render_phase_panel(environment: SyntheticRFEnvironment) -> None:
    section_header("ENVIRONMENT STATE", "Synthetic scenario configuration")
    if environment.config.name == "changing":
        shift = environment.num_steps // 2
        st.markdown(
            f'<div class="surface"><div class="boundary-note">The changing scenario is generated in two descriptive phases; the scheduler receives observations from the simulated receiver, not this reference activity.</div><div class="phase-line"><div class="phase-block"><div class="mono-label">PHASE 01</div><strong>t = 0–{shift - 1}</strong><div class="boundary-note">Early activity pattern</div></div><div class="phase-shift">SCENARIO SHIFT<br>t = {shift}</div><div class="phase-block"><div class="mono-label">PHASE 02</div><strong>t = {shift}–{environment.num_steps - 1}</strong><div class="boundary-note">Later activity pattern</div></div></div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="surface"><div class="boundary-note"><strong>{environment.config.name.title()}</strong> is the active synthetic scenario. The reference activity is shown for evaluation context; scheduler decisions use simulated receiver observations.</div></div>',
            unsafe_allow_html=True,
        )


def render_run_configuration(
    scenario: str,
    bands: int,
    steps: int,
    seed: int,
    receiver: object,
) -> None:
    st.markdown(
        '<div class="surface"><div class="section-label">RUN CONFIGURATION</div><div class="summary-grid">',
        unsafe_allow_html=True,
    )
    values = [
        ("Scenario", scenario.title()),
        ("Bands", str(bands)),
        ("Time steps", str(steps)),
        ("Seed", str(seed)),
        ("P(detection)", f"{receiver.detection_probability:.2f}"),
        ("P(false alarm)", f"{receiver.false_alarm_probability:.2f}"),
    ]
    for label, value in values:
        st.markdown(
            f'<div class="summary-item"><div class="mono-label">{label}</div><div class="summary-value">{value}</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_information_boundary() -> None:
    with st.expander("TRUTH VS OBSERVATION", expanded=False):
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("**REFERENCE ACTIVITY**")
            st.caption("Synthetic ground truth used only for evaluation and visualization.")
        with right:
            st.markdown("**OBSERVED FEEDBACK**")
            st.caption("Receiver detections returned to the scheduler after each scan.")


def render_methodology() -> None:
    with st.expander("HOW WAS THIS EVALUATED?", expanded=False):
        st.markdown(
            "- Identical scenario conditions\n"
            "- Identical number of bands and time horizon\n"
            "- Same random seed\n"
            "- Same simulated receiver model\n"
            "- One simulation run per strategy\n"
            "- Event metrics calculated from that run's scan history"
        )


def render_key_findings() -> None:
    findings = load_held_out_findings()
    section_header("KEY FINDINGS", "Synthetic multi-seed evaluation")
    if findings.empty:
        st.caption("Held-out multi-seed summary data is not available.")
        return

    rows = []
    for scenario in HELD_OUT_SCENARIOS:
        scenario_rows = findings[findings["scenario"].eq(scenario)].set_index("strategy")
        if not {"Adaptive", "Smart Adaptive"}.issubset(scenario_rows.index):
            continue
        adaptive = scenario_rows.loc["Adaptive", "mean"]
        smart = scenario_rows.loc["Smart Adaptive", "mean"]
        rows.append(
            {
                "Scenario": scenario.title(),
                "Adaptive": f"{adaptive * 100:.2f}%",
                "Smart Adaptive": f"{smart * 100:.2f}%",
                "Improvement": f"{(smart - adaptive) * 100:+.2f} pp",
            }
        )

    if rows:
        st.markdown(
            '<table class="findings-table"><thead><tr><th>Scenario</th><th>Adaptive</th><th>Smart Adaptive</th><th>Difference</th></tr></thead><tbody>'
            + "".join(
                f"<tr><td>{row['Scenario']}</td><td>{row['Adaptive']}</td><td>{row['Smart Adaptive']}</td><td>{row['Improvement']}</td></tr>"
                for row in rows
            )
            + "</tbody></table>",
            unsafe_allow_html=True,
        )
    st.caption("Smart Adaptive improved event interception over the simple Adaptive baseline across the evaluated held-out synthetic scenarios.")


def make_heatmap(environment: SyntheticRFEnvironment, title: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9.5, 3.7), dpi=120)
    fig.patch.set_facecolor("#ffffff")
    image = ax.imshow(environment.activity.T, aspect="auto", interpolation="nearest", cmap="magma", vmin=0, vmax=1)
    ax.set_title(title, loc="left", fontsize=10, color="#151515", pad=10, fontweight="bold")
    ax.set_xlabel("Time step", fontsize=8, color="#777771")
    ax.set_ylabel("Frequency band", fontsize=8, color="#777771")
    ax.set_yticks(range(environment.num_bands))
    ax.set_yticklabels([f"B{i + 1}" for i in range(environment.num_bands)], fontsize=6, color="#777771")
    ax.tick_params(axis="x", labelsize=7, colors="#777771")
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.colorbar(image, ax=ax, fraction=.018, pad=.02, ticks=[0, 1])
    fig.tight_layout(pad=1.1)
    return fig


def make_strategy_chart(data: pd.DataFrame, metric: str) -> plt.Figure:
    colors = ["#b3b8ae" if name != "Smart Adaptive" else "#d71920" for name in data["Strategy"]]
    fig, ax = plt.subplots(figsize=(8, 3.1), dpi=120)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")
    ax.bar(data["Strategy"], data[metric], color=colors, width=.58)
    ax.set_ylabel(metric, fontsize=8, color="#777771")
    ax.tick_params(axis="x", labelsize=8, colors="#555550")
    ax.tick_params(axis="y", labelsize=8, colors="#777771")
    ax.grid(axis="y", color="#eceae5", linewidth=.8)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout(pad=1.2)
    return fig


def make_priority_chart(scores: list[float], selected: int | None = None) -> plt.Figure:
    labels = [f"B{i + 1}" for i in range(len(scores))]
    colors = ["#d71920" if i == selected else "#b3b8ae" for i in range(len(scores))]
    fig, ax = plt.subplots(figsize=(8, 3.4), dpi=120)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")
    ax.bar(labels, scores, color=colors, width=.72)
    ax.set_ylabel("Priority score", fontsize=8, color="#777771")
    ax.tick_params(axis="x", labelsize=7, colors="#777771")
    ax.tick_params(axis="y", labelsize=8, colors="#777771")
    ax.grid(axis="y", color="#eceae5", linewidth=.8)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout(pad=1.1)
    return fig


def sidebar_controls() -> tuple[str, str, int, int, int]:
    with st.sidebar:
        st.markdown('<div class="eyebrow">SIH26055</div><h2>Smart Scan Strategy</h2><p class="section-note">SYNTHETIC RF ENVIRONMENT</p>', unsafe_allow_html=True)
        st.markdown("---")
        mode = st.radio("Workspace", ["Benchmark", "Live Adaptive Demo", "Final Demo"], label_visibility="collapsed")
        st.markdown('<div class="section-label sidebar-controls-label">SIMULATION CONTROLS</div>', unsafe_allow_html=True)
        scenario = st.selectbox("Scenario", SCENARIOS, index=0)
        bands = st.slider("Frequency bands", 10, 30, 20)
        steps = st.slider("Time steps", 50, 300, 100)
        seed = int(st.number_input("Random seed", min_value=0, value=42, step=1))
        st.markdown("---")
        st.markdown('<div class="mono-label"><span class="synthetic-dot">●</span> SYNTHETIC ONLY<br>Academic project // reproducible runs</div>', unsafe_allow_html=True)
    return mode, scenario, bands, steps, seed


def benchmark_table(results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for name in STRATEGIES:
        basic = results[name]["basic"]
        events = results[name]["events"]
        rows.append({"Strategy": name, "Detection Probability": f"{basic.detection_probability * 100:.2f}%", "False Alarm Probability": f"{basic.false_alarm_probability * 100:.2f}%", "Interception Ratio": f"{events.interception_ratio * 100:.2f}%", "Average Intercept": f"{events.average_intercept_delay:.2f}", "Average Reward": f"{basic.average_reward:.3f}", "Coverage": f"{basic.coverage * 100:.2f}%"})
    return pd.DataFrame(rows)


def benchmark_export_payload(results: dict[str, dict]) -> list[dict[str, object]]:
    rows = []
    for name in STRATEGIES:
        basic = results[name]["basic"]
        events = results[name]["events"]
        rows.append(
            {
                "strategy": name,
                "detection_probability": basic.detection_probability,
                "false_alarm_probability": basic.false_alarm_probability,
                "interception_ratio": events.interception_ratio,
                "average_intercept_delay": events.average_intercept_delay,
                "average_reward": basic.average_reward,
                "coverage": basic.coverage,
            }
        )
    return rows


def render_benchmark(environment: SyntheticRFEnvironment, scenario: str, bands: int, steps: int, seed: int) -> None:
    app_header("BENCHMARK // STRATEGY EVALUATION")
    signature = (scenario, bands, steps, seed)
    if st.session_state.get("benchmark_signature") != signature:
        st.session_state.benchmark_results = None
        st.session_state.benchmark_signature = signature
    run_button = st.sidebar.button("Run benchmark", type="primary", width="stretch")
    if run_button or st.session_state.get("benchmark_results") is None:
        with st.spinner("Evaluating four schedulers on identical conditions..."):
            st.session_state.benchmark_results = run_benchmark(scenario, bands, steps, seed)
    results = st.session_state.benchmark_results
    smart_basic = results["Smart Adaptive"]["basic"]
    smart_events = results["Smart Adaptive"]["events"]

    section_header("SMART ADAPTIVE // KEY OUTCOMES", "Proposed strategy")
    kpis = st.columns(4)
    values = [("Detection probability", f"{smart_basic.detection_probability * 100:.2f}%"), ("False alarm probability", f"{smart_basic.false_alarm_probability * 100:.2f}%"), ("Event interception", f"{smart_events.interception_ratio * 100:.2f}%"), ("Average reward", f"{smart_basic.average_reward:.3f}")]
    for column, (label, value) in zip(kpis, values):
        with column:
            metric_card(label, value, accent=label == "Event interception")

    section_header("SPECTRUM ACTIVITY", f"{scenario.title()} scenario // {steps} time steps")
    spectrum_col, summary_col = st.columns([2.25, 1], gap="large")
    with spectrum_col:
        st.pyplot(make_heatmap(environment, "Reference activity across time and frequency"), width="stretch")
    with summary_col:
        st.markdown('<div class="surface"><div class="section-label">EXPERIMENT</div><div class="summary-grid">', unsafe_allow_html=True)
        for label, value in [("Scenario", scenario.title()), ("Bands", str(bands)), ("Time steps", str(steps)), ("Seed", str(seed))]:
            st.markdown(f'<div class="summary-item"><div class="mono-label">{label}</div><div class="summary-value">{value}</div></div>', unsafe_allow_html=True)
        st.markdown('</div><div class="summary-note">Four scheduling strategies are evaluated under identical synthetic conditions.</div></div>', unsafe_allow_html=True)
        render_run_configuration(scenario, bands, steps, seed, SimulatedReceiver(environment))

    render_information_boundary()
    render_phase_panel(environment)

    section_header("SCHEDULER COMPARISON", "Lower visual weight for baselines")
    data = pd.DataFrame({"Strategy": STRATEGIES, "Detection Probability": [results[name]["basic"].detection_probability * 100 for name in STRATEGIES], "Interception Ratio": [results[name]["events"].interception_ratio * 100 for name in STRATEGIES]})
    chart_col, chart_col2 = st.columns(2, gap="large")
    with chart_col:
        st.pyplot(make_strategy_chart(data, "Detection Probability"), width="stretch")
    with chart_col2:
        st.pyplot(make_strategy_chart(data, "Interception Ratio"), width="stretch")

    section_header("BENCHMARK RESULTS", "One reproducible run // all values from runtime state")
    result_df = benchmark_table(results)
    styled = result_df.style.apply(lambda row: ["color:#d71920;font-weight:600" if row["Strategy"] == "Smart Adaptive" else "" for _ in row], axis=1)
    st.dataframe(styled, width="stretch", hide_index=True)

    export_col, export_col2 = st.columns([1, 1])
    raw_payload = benchmark_export_payload(results)
    with export_col:
        st.download_button(
            "Download results CSV",
            data=result_df.to_csv(index=False),
            file_name=f"sih26055_{scenario}_benchmark.csv",
            mime="text/csv",
            width="stretch",
        )
    with export_col2:
        st.download_button(
            "Download summary JSON",
            data=json.dumps({"scenario": scenario, "bands": bands, "steps": steps, "seed": seed, "results": raw_payload}, indent=2),
            file_name=f"sih26055_{scenario}_benchmark.json",
            mime="application/json",
            width="stretch",
        )

    section_header("SCAN ALLOCATION", "Where each strategy spent its scan opportunities")
    allocation_histories = get_scan_histories(scenario, bands, steps, seed)
    st.pyplot(make_allocation_chart(allocation_histories, bands), width="stretch")
    render_key_findings()
    render_methodology()


def get_runner(environment: SyntheticRFEnvironment, seed: int, key: str) -> DemoRunner:
    existing = st.session_state.get(key)
    signature = (environment.seed, environment.config.name, environment.num_steps, environment.num_bands)
    if existing is None or st.session_state.get(f"{key}_signature") != signature:
        existing = DemoRunner(environment=environment, seed=seed)
        st.session_state[key] = existing
        st.session_state[f"{key}_signature"] = signature
        state_key = "final_demo_state" if key == "final_demo_runner" else "demo_state"
        st.session_state[state_key] = None
    return existing


def render_live(environment: SyntheticRFEnvironment, scenario: str, bands: int, steps: int, seed: int) -> None:
    app_header("LIVE SIMULATION // ADAPTIVE DECISION LOOP")
    runner = get_runner(environment, seed, "demo_runner")
    controls = st.columns([1, 1, 1, 2])
    with controls[0]:
        next_scan = st.button("Next scan", type="primary", width="stretch")
    with controls[1]:
        run_all = st.button("Run full demo", width="stretch")
    with controls[2]:
        reset = st.button("Reset", width="stretch")
    with controls[3]:
        st.caption(f"{scenario.title()} // {bands} bands // {steps} steps // seed {seed}")
    if reset:
        st.session_state.demo_runner = DemoRunner(environment=environment, seed=seed)
        st.session_state.demo_runner_signature = (environment.seed, scenario, steps, bands)
        st.session_state.demo_state = None
        st.rerun()
    if next_scan:
        st.session_state.demo_state = runner.step()
    if run_all:
        while not runner.state.finished:
            st.session_state.demo_state = runner.step()

    state = st.session_state.get("demo_state")
    section_header("CURRENT DECISION", "Observe → learn → respond")
    decision_col, explain_col = st.columns([1, 1.8], gap="large")
    with decision_col:
        band_text = f"B{state.selected_band + 1:02d}" if state and state.selected_band is not None else "--"
        detected_text = "DETECTED" if state and state.detected else "WAITING"
        reward_text = f"{state.reward:+.1f}" if state else "--"
        step_text = f"{state.time_step + 1} / {steps}" if state else f"0 / {steps}"
        status_text = "Complete" if runner.state.finished else "Ready"
        st.markdown(f'<div class="surface"><div class="mono-label">SELECTED BAND</div><div class="decision-band"><em>{band_text}</em></div><div class="summary-grid"><div class="summary-item"><div class="mono-label">Time step</div><div class="summary-value">{step_text}</div></div><div class="summary-item"><div class="mono-label">Detection</div><div class="summary-value">{detected_text}</div></div><div class="summary-item"><div class="mono-label">Reward</div><div class="summary-value">{reward_text}</div></div><div class="summary-item"><div class="mono-label">Status</div><div class="summary-value">{status_text}</div></div></div></div>', unsafe_allow_html=True)
    with explain_col:
        section_header("WHY THIS BAND?", "Scheduler-derived signals")
        scheduler = runner.scheduler
        scores = runner.get_scores()
        selected = state.selected_band if state else None
        if selected is not None:
            explanation = runner.get_band_explanation(selected)
            explain_df = pd.DataFrame(
                {
                    "Signal": [
                        "Recent activity",
                        "Uncertainty",
                        "Scan age",
                        "Activity contribution",
                        "Uncertainty contribution",
                        "Scan-age contribution",
                        "Final priority",
                    ],
                    "Value": [
                        explanation["activity"],
                        explanation["uncertainty"],
                        explanation["age"],
                        explanation["activity_contribution"],
                        explanation["uncertainty_contribution"],
                        explanation["age_contribution"],
                        explanation["final_priority"],
                    ],
                }
            )
            explain_df["Value"] = explain_df["Value"].map(lambda value: f"{value:.3f}")
            st.markdown(f"**Selected band: B{selected + 1:02d}**")
            st.dataframe(explain_df, width="stretch", hide_index=True)
            st.caption("Final priority = 0.60 × activity + 0.15 × uncertainty + 0.25 × age. All signals come from scheduler observations.")
        else:
            st.caption("Run the first scan to expose the scheduler's observed signals.")

    section_header("BAND PRIORITIES", "Current Smart Adaptive scores")
    st.pyplot(make_priority_chart(runner.get_scores(), state.selected_band if state else None), width="stretch")
    render_phase_panel(environment)
    section_header("RUN STATUS", "Live simulation")
    status = "COMPLETE" if runner.state.finished else ("RUNNING" if state else "READY")
    st.markdown(f'<div class="status-ready">● {status}</div>', unsafe_allow_html=True)
    history = runner.get_history()
    if history:
        section_header("SCAN HISTORY", "Most recent observations")
        rows = [{"Time": record.time_step, "Band": f"B{record.band + 1:02d}", "Truth active": "Yes" if record.truth_active else "No", "Detected": "Yes" if record.detected else "No", "False alarm": "Yes" if record.false_alarm else "No"} for record in history[-10:]]
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        if len(history) > 1:
            path_df = pd.DataFrame({"Time": [record.time_step for record in history], "Band": [record.band + 1 for record in history]})
            st.line_chart(path_df.set_index("Time"), y="Band", color="#d71920", width="stretch")


def render_final_demo() -> None:
    scenario, bands, steps, seed = "changing", 20, 100, 42
    environment = make_environment(scenario, bands, steps, seed)
    app_header("FINAL DEMO // PRESENTATION VIEW")
    st.markdown('<div class="final-title">Adaptive scan scheduling</div><div class="header-subtitle">A controlled synthetic environment for observing, learning, and responding.</div><div class="flow">OBSERVE &nbsp;→&nbsp; LEARN &nbsp;→&nbsp; RESPOND</div>', unsafe_allow_html=True)
    runner = get_runner(environment, seed, "final_demo_runner")
    controls = st.columns([1, 1, 3])
    with controls[0]:
        next_scan = st.button("Next scan", type="primary", width="stretch", key="final_next")
    with controls[1]:
        run_demo = st.button("Run demo", width="stretch", key="final_run")
    with controls[2]:
        st.caption("Fixed presentation run // changing scenario // 20 bands // seed 42")
    if st.button("Reset final demo", key="final_reset"):
        st.session_state.final_demo_runner = DemoRunner(environment=environment, seed=seed)
        st.session_state.final_demo_runner_signature = (environment.seed, scenario, steps, bands)
        st.session_state.final_demo_state = None
        st.rerun()
    if next_scan:
        st.session_state.final_demo_state = runner.step()
    if run_demo:
        while not runner.state.finished:
            st.session_state.final_demo_state = runner.step()
    state = st.session_state.get("final_demo_state")

    section_header("SPECTRUM ACTIVITY", "Changing scenario // fixed reference run")
    visual_col, decision_col = st.columns([2.25, 1], gap="large")
    with visual_col:
        st.pyplot(make_heatmap(environment, "Activity reference // changing scenario"), width="stretch")
    with decision_col:
        band = f"B{state.selected_band + 1:02d}" if state and state.selected_band is not None else "--"
        detection = "DETECTED" if state and state.detected else "WAITING"
        reward = f"{state.reward:+.1f}" if state else "--"
        time_step = state.time_step + 1 if state else 0
        st.markdown(f'<div class="surface"><div class="section-label">CURRENT DECISION</div><div class="decision-band"><em>{band}</em></div><div class="decision-copy">Time step {time_step} / {steps}<br>Observation: {detection}<br>Reward: {reward}</div></div>', unsafe_allow_html=True)

    render_information_boundary()
    render_phase_panel(environment)
    section_header("WHY THIS BAND?", "Observable scheduler decomposition")
    if state and state.selected_band is not None:
        explanation = runner.get_band_explanation(state.selected_band)
        explanation_df = pd.DataFrame(
            {
                "Signal": ["Recent activity", "Uncertainty", "Scan age", "Final priority"],
                "Value": [explanation["activity"], explanation["uncertainty"], explanation["age"], explanation["final_priority"]],
            }
        )
        explanation_df["Value"] = explanation_df["Value"].map(lambda value: f"{value:.3f}")
        st.dataframe(explanation_df, width="stretch", hide_index=True)
    else:
        st.caption("Run the demo to expose the scheduler's observed decision signals.")

    section_header("BAND PRIORITIES", "Live scheduler state")
    st.pyplot(make_priority_chart(runner.get_scores(), state.selected_band if state else None), width="stretch")
    allocation_histories = get_scan_histories(scenario, bands, steps, seed)
    section_header("SCAN ALLOCATION", "Actual scan opportunities by strategy")
    st.pyplot(make_allocation_chart(allocation_histories, bands), width="stretch")
    final_results = run_benchmark(scenario, bands, steps, seed)
    smart = final_results["Smart Adaptive"]
    section_header("FINAL RESULTS", "Fixed run // actual evaluation metrics")
    result_cols = st.columns(4)
    values = [("Detection", f"{smart['basic'].detection_probability * 100:.2f}%"), ("Interception", f"{smart['events'].interception_ratio * 100:.2f}%"), ("Average reward", f"{smart['basic'].average_reward:.3f}"), ("Coverage", f"{smart['basic'].coverage * 100:.2f}%")]
    for column, (label, value) in zip(result_cols, values):
        with column:
            metric_card(label, value, accent=label == "Interception")
    render_key_findings()
    render_methodology()


def main() -> None:
    st.set_page_config(page_title="SIH26055 Smart Scan Strategy", page_icon="◉", layout="wide", initial_sidebar_state="expanded")
    apply_theme()
    for key, default in [("benchmark_results", None), ("demo_state", None), ("final_demo_state", None)]:
        if key not in st.session_state:
            st.session_state[key] = default
    mode, scenario, bands, steps, seed = sidebar_controls()
    environment = make_environment(scenario, bands, steps, seed)
    if mode == "Benchmark":
        render_benchmark(environment, scenario, bands, steps, seed)
    elif mode == "Live Adaptive Demo":
        render_live(environment, scenario, bands, steps, seed)
    else:
        render_final_demo()


if __name__ == "__main__":
    main()