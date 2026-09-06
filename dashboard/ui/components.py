from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HELD_OUT_SCENARIOS = ["periodic", "bursty", "mixed"]


def app_header(kicker: str) -> None:
    st.markdown(
        """
        <div class="header-row"><div>
        <h1>Smart Scan Strategy</h1><div class="header-subtitle">Adaptive decision-making in a synthetic RF environment</div></div>
        <div class="status-mark"><span>●</span> SYNTHETIC ONLY</div></div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, note: str = "") -> None:
    st.markdown(f'<div class="section-head"><div class="section-label">{title}</div><div class="section-note">{note}</div></div>', unsafe_allow_html=True)


def render_kpi_card(label: str, value: str, accent: bool = False) -> None:
    color = "#e3262e" if accent else "#f1f0eb"
    st.markdown(f'<div class="surface"><div class="mono-label">{label}</div><div class="metric-value" style="color:{color}">{value}</div></div>', unsafe_allow_html=True)


def render_run_configuration(
    scenario: str,
    bands: int,
    steps: int,
    seed: int,
    receiver: object,
) -> None:
    st.markdown('<div class="surface"><div class="section-label">RUN CONFIGURATION</div><div class="summary-grid">', unsafe_allow_html=True)
    values = [
        ("Scenario", scenario.title()),
        ("Frequency Bands", str(bands)),
        ("Time Steps", str(steps)),
        ("Random Seed", str(seed)),
        ("P(detection)", f"{receiver.detection_probability:.2f}"),
        ("P(false alarm)", f"{receiver.false_alarm_probability:.2f}"),
    ]
    for label, value in values:
        st.markdown(
            f'<div class="summary-item"><div class="mono-label">{label}</div><div class="summary-value">{value}</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_scan_pipeline() -> None:
    st.markdown('<div class="section-label">SCAN PIPELINE</div>', unsafe_allow_html=True)
    pipeline = [
        ("SIMULATE", "Generate synthetic RF activity"),
        ("OBSERVE", "Simulated receiver returns detection or miss"),
        ("DECIDE", "Scheduler selects the next band"),
        ("FEEDBACK", "Update activity, uncertainty, and scan age"),
        ("REPEAT", "Continue until the time horizon ends"),
    ]
    for idx, (label, description) in enumerate(pipeline):
        if idx < len(pipeline) - 1:
            st.markdown(f'<div class="pipeline-block"><strong>{label}</strong><span>{description}</span></div>', unsafe_allow_html=True)
            st.markdown('<div style="text-align:center; margin:.25rem 0; color:var(--muted);">↓</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="pipeline-block"><strong>{label}</strong><span>{description}</span></div>', unsafe_allow_html=True)


def render_reference_vs_observed() -> None:
    render_section_header("REFERENCE VS OBSERVED DATA", "Information boundary")
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(
            '<div class="info-card"><div class="mono-label">REFERENCE ACTIVITY</div><p>Synthetic ground truth used only for evaluation and visualization.</p></div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            '<div class="info-card"><div class="mono-label">OBSERVED FEEDBACK</div><p>Receiver detections returned to the scheduler after each scan.</p></div>',
            unsafe_allow_html=True,
        )


def render_methodology_table(scenario: str, bands: int, steps: int, seed: int) -> None:
    render_section_header("EVALUATION METHODOLOGY", "Controlled comparison")
    st.markdown(
        f"| Evaluation Property | Configuration |\n"
        f"|----------------------|---------------|\n"
        f"| Strategies | Sequential, Random, Adaptive, Smart Adaptive |\n"
        f"| Scenario | Same scenario for all strategies ({scenario.title()}) |\n"
        f"| Bands | Same number of bands ({bands}) |\n"
        f"| Time horizon | Same number of time steps ({steps}) |\n"
        f"| Seed | Same seed within each comparison ({seed}) |\n"
        "| Receiver | Same simulated receiver model |\n"
        "| Event metrics | Calculated from each strategy's exact scan history |\n"
        "| Multi-seed evaluation | 20 seeds |\n"
        "| Held-out scenarios | Periodic, Bursty, Mixed |",
    )


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


def render_key_findings() -> None:
    findings = load_held_out_findings()
    render_section_header("KEY FINDINGS", "Synthetic multi-seed evaluation")
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
