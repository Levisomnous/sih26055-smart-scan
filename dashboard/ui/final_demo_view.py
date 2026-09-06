from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.demo_runner import DemoRunner
from dashboard.ui.benchmark_view import make_allocation_chart, make_environment, get_scan_histories, make_heatmap
from dashboard.ui.components import app_header, render_key_findings, render_kpi_card, render_methodology_table, render_reference_vs_observed, render_section_header
from evaluation.benchmark import run_benchmark
from dashboard.ui.live_view import get_runner


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

    render_section_header("SPECTRUM ACTIVITY", "Changing scenario // fixed reference run")
    visual_col, decision_col = st.columns([2.25, 1], gap="large")
    with visual_col:
        st.pyplot(make_heatmap(environment, "Activity reference // changing scenario"), width="stretch")
    with decision_col:
        band = f"B{state.selected_band + 1:02d}" if state and state.selected_band is not None else "--"
        detection = "DETECTED" if state and state.detected else "WAITING"
        reward = f"{state.reward:+.1f}" if state else "--"
        time_step = state.time_step + 1 if state else 0
        status = "RUNNING" if not runner.state.finished else "COMPLETE"
        st.markdown(
            f'<div class="surface"><div class="section-label">CURRENT DECISION</div><div class="decision-band"><em>{band}</em></div>'
            f'<div class="summary-grid"><div class="summary-item"><div class="mono-label">Time step</div><div class="summary-value">{time_step} / {steps}</div></div>'
            f'<div class="summary-item"><div class="mono-label">Detection</div><div class="summary-value">{detection}</div></div>'
            f'<div class="summary-item"><div class="mono-label">Reward</div><div class="summary-value">{reward}</div></div>'
            f'<div class="summary-item"><div class="mono-label">Status</div><div class="summary-value">{status}</div></div></div></div>',
            unsafe_allow_html=True,
        )

    render_reference_vs_observed()
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

    render_section_header("WHY THIS BAND?", "Observable scheduler decomposition")
    if state and state.selected_band is not None:
        explanation = runner.get_band_explanation(state.selected_band)
        explanation_df = pd.DataFrame(
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
        explanation_df["Value"] = explanation_df["Value"].map(lambda value: f"{value:.3f}")
        st.dataframe(explanation_df, width="stretch", hide_index=True)
        st.caption("Final priority = 0.60 × activity + 0.15 × uncertainty + 0.25 × age. All signals come from scheduler observations.")
    else:
        st.caption("Run the demo to expose the scheduler's observed decision signals.")

    render_section_header("BAND PRIORITIES", "Live scheduler state")
    import matplotlib.pyplot as plt
    from dashboard.ui.live_view import make_priority_chart
    st.pyplot(make_priority_chart(runner.get_scores(), state.selected_band if state else None), width="stretch")
    allocation_histories = get_scan_histories(scenario, bands, steps, seed)
    render_section_header("SCAN ALLOCATION", "Actual scan opportunities by strategy")
    st.pyplot(make_allocation_chart(allocation_histories, bands), width="stretch")
    final_results = run_benchmark(scenario, bands, steps, seed)
    smart = final_results["Smart Adaptive"]
    render_section_header("FINAL RESULTS", "Fixed run // actual evaluation metrics")
    result_cols = st.columns(4)
    values = [
        ("Detection", f"{smart['basic'].detection_probability * 100:.2f}%"),
        ("Interception", f"{smart['events'].interception_ratio * 100:.2f}%"),
        ("Average reward", f"{smart['basic'].average_reward:.3f}"),
        ("Coverage", f"{smart['basic'].coverage * 100:.2f}%"),
    ]
    for column, (label, value) in zip(result_cols, values):
        with column:
            render_kpi_card(label, value, accent=label == "Interception")
    render_key_findings()
    render_methodology_table(scenario, bands, steps, seed)
