from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.demo_runner import DemoRunner
from dashboard.ui.components import (
    app_header,
    render_reference_vs_observed,
    render_run_configuration,
    render_section_header,
)
from simulator.environment import SyntheticRFEnvironment


def make_priority_chart(scores: list[float], selected: int | None = None) -> object:
    import matplotlib.pyplot as plt

    labels = [f"B{i + 1}" for i in range(len(scores))]
    colors = ["#e3262e" if i == selected else "#9ea4a5" for i in range(len(scores))]
    fig, ax = plt.subplots(figsize=(8, 3.4), dpi=120)
    fig.patch.set_facecolor("#0d1012")
    ax.set_facecolor("#0d1012")
    ax.bar(labels, scores, color=colors, width=.72)
    ax.set_ylabel("Priority score", fontsize=8, color="#9ea4a5")
    ax.tick_params(axis="x", labelsize=7, colors="#9ea4a5")
    ax.tick_params(axis="y", labelsize=8, colors="#9ea4a5")
    ax.grid(axis="y", color="#2a3235", linewidth=.8)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.title.set_color("#f1f0eb")
    fig.tight_layout(pad=1.1)
    return fig


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


def render_live_demo(environment: SyntheticRFEnvironment, scenario: str, bands: int, steps: int, seed: int) -> None:
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
    render_section_header("CURRENT DECISION", "Observe → learn → respond")
    decision_col, explain_col = st.columns([1, 1.8], gap="large")
    with decision_col:
        band_text = f"B{state.selected_band + 1:02d}" if state and state.selected_band is not None else "--"
        detected_text = "DETECTED" if state and state.detected else "WAITING"
        reward_text = f"{state.reward:+.1f}" if state else "--"
        step_text = f"{state.time_step + 1} / {steps}" if state else f"0 / {steps}"
        status_text = "Complete" if runner.state.finished else "Ready"
        st.markdown(f'<div class="surface"><div class="mono-label">SELECTED BAND</div><div class="decision-band"><em>{band_text}</em></div><div class="summary-grid"><div class="summary-item"><div class="mono-label">Time step</div><div class="summary-value">{step_text}</div></div><div class="summary-item"><div class="mono-label">Detection</div><div class="summary-value">{detected_text}</div></div><div class="summary-item"><div class="mono-label">Reward</div><div class="summary-value">{reward_text}</div></div><div class="summary-item"><div class="mono-label">Status</div><div class="summary-value">{status_text}</div></div></div></div>', unsafe_allow_html=True)
    with explain_col:
        render_section_header("WHY THIS BAND?", "Scheduler-derived signals")
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

    render_section_header("BAND PRIORITIES", "Current Smart Adaptive scores")
    st.pyplot(make_priority_chart(runner.get_scores(), state.selected_band if state else None), width="stretch")
    render_section_header("ENVIRONMENT STATE", "Synthetic scenario configuration")
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
    render_section_header("RUN STATUS", "Live simulation")
    status = "COMPLETE" if runner.state.finished else ("RUNNING" if state else "READY")
    st.markdown(f'<div class="status-ready">● {status}</div>', unsafe_allow_html=True)
    history = runner.get_history()
    if history:
        render_section_header("SCAN HISTORY", "Most recent observations")
        rows = [{"Time": record.time_step, "Band": f"B{record.band + 1:02d}", "Truth active": "Yes" if record.truth_active else "No", "Detected": "Yes" if record.detected else "No", "False alarm": "Yes" if record.false_alarm else "No"} for record in history[-10:]]
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        if len(history) > 1:
            path_df = pd.DataFrame({"Time": [record.time_step for record in history], "Band": [record.band + 1 for record in history]})
            st.line_chart(path_df.set_index("Time"), y="Band", color="#e3262e", width="stretch")
