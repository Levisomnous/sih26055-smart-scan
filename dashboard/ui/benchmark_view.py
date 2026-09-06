from __future__ import annotations

import json

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from dashboard.demo_runner import DemoRunner
from dashboard.ui.components import (
    app_header,
    render_key_findings,
    render_kpi_card,
    render_methodology_table,
    render_reference_vs_observed,
    render_run_configuration,
    render_scan_pipeline,
    render_section_header,
)
from evaluation.benchmark import default_scheduler_factories, run_benchmark
from evaluation.runner import run_scheduler_with_history
from simulator.environment import ScenarioConfig, SyntheticRFEnvironment
from simulator.receiver import SimulatedReceiver

SCENARIOS = ["changing", "persistent", "periodic", "bursty", "mixed"]
STRATEGIES = ["Sequential", "Random", "Adaptive", "Smart Adaptive"]
STRATEGY_COLORS = {
    "Sequential": "#9ea4a5",
    "Random": "#8b9396",
    "Adaptive": "#687174",
    "Smart Adaptive": "#e3262e",
}


def make_environment(scenario: str, bands: int, steps: int, seed: int) -> SyntheticRFEnvironment:
    return SyntheticRFEnvironment(ScenarioConfig(scenario, bands, steps, seed))


def get_scan_histories(scenario: str, bands: int, steps: int, seed: int) -> dict[str, list]:
    histories: dict[str, list] = {}
    for name, create_scheduler in default_scheduler_factories(bands, seed).items():
        environment = make_environment(scenario, bands, steps, seed)
        _, history = run_scheduler_with_history(environment, create_scheduler())
        histories[name] = history
    return histories


def make_allocation_chart(histories: dict[str, list], bands: int) -> plt.Figure:
    counts = pd.DataFrame(0, index=range(1, bands + 1), columns=STRATEGIES)
    for strategy, history in histories.items():
        for record in history:
            counts.loc[record.band + 1, strategy] += 1

    fig, ax = plt.subplots(figsize=(9.5, 3.8), dpi=120)
    fig.patch.set_facecolor("#0d1012")
    ax.set_facecolor("#0d1012")
    counts.plot.bar(
        ax=ax,
        width=.82,
        color=[STRATEGY_COLORS[strategy] for strategy in STRATEGIES],
    )
    ax.set_xlabel("Frequency band", fontsize=8, color="#9ea4a5")
    ax.set_ylabel("Scan opportunities", fontsize=8, color="#9ea4a5")
    ax.tick_params(axis="x", labelsize=7, colors="#9ea4a5", rotation=0)
    ax.tick_params(axis="y", labelsize=8, colors="#9ea4a5")
    ax.grid(axis="y", color="#2a3235", linewidth=.8)
    ax.set_axisbelow(True)
    legend = ax.legend(frameon=False, fontsize=7, ncol=4, loc="upper center", bbox_to_anchor=(.5, 1.13))
    for text in legend.get_texts():
        text.set_color("#f1f0eb")
    legend.get_frame().set_facecolor("#151a1d")
    legend.get_frame().set_edgecolor("#2a3235")
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout(pad=1.2)
    return fig


def make_heatmap(environment: SyntheticRFEnvironment, title: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9.5, 3.7), dpi=120)
    fig.patch.set_facecolor("#0d1012")
    ax.set_facecolor("#0d1012")
    image = ax.imshow(environment.activity.T, aspect="auto", interpolation="nearest", cmap="inferno", vmin=0, vmax=1)
    ax.set_title(title, loc="left", fontsize=10, color="#f1f0eb", pad=10, fontweight="bold")
    ax.set_xlabel("Time step", fontsize=8, color="#9ea4a5")
    ax.set_ylabel("Frequency band", fontsize=8, color="#9ea4a5")
    ax.set_yticks(range(environment.num_bands))
    ax.set_yticklabels([f"B{i + 1}" for i in range(environment.num_bands)], fontsize=6, color="#9ea4a5")
    ax.tick_params(axis="x", labelsize=7, colors="#9ea4a5")
    ax.tick_params(axis="y", colors="#9ea4a5")
    for spine in ax.spines.values():
        spine.set_visible(False)
    cbar = fig.colorbar(image, ax=ax, fraction=.018, pad=.02, ticks=[0, 1])
    cbar.ax.tick_params(colors="#9ea4a5", labelsize=7)
    cbar.outline.set_edgecolor("#2a3235")
    cbar.ax.yaxis.label.set_color("#f1f0eb")
    fig.tight_layout(pad=1.1)
    return fig


def make_strategy_chart(data: pd.DataFrame, metric: str) -> plt.Figure:
    colors = ["#9ea4a5" if name != "Smart Adaptive" else "#e3262e" for name in data["Strategy"]]
    fig, ax = plt.subplots(figsize=(8, 3.1), dpi=120)
    fig.patch.set_facecolor("#0d1012")
    ax.set_facecolor("#0d1012")
    ax.bar(data["Strategy"], data[metric], color=colors, width=.58)
    ax.set_ylabel(metric, fontsize=8, color="#9ea4a5")
    ax.tick_params(axis="x", labelsize=8, colors="#f1f0eb")
    ax.tick_params(axis="y", labelsize=8, colors="#9ea4a5")
    ax.grid(axis="y", color="#2a3235", linewidth=.8)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    leg = ax.legend(frameon=False, fontsize=8)
    for text in leg.get_texts():
        text.set_color("#f1f0eb")
    if leg.get_frame() is not None:
        leg.get_frame().set_facecolor("#151a1d")
        leg.get_frame().set_edgecolor("#2a3235")
    fig.tight_layout(pad=1.2)
    return fig


def benchmark_table(results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for name in STRATEGIES:
        basic = results[name]["basic"]
        events = results[name]["events"]
        rows.append({
            "Strategy": name,
            "Detection Probability": f"{basic.detection_probability * 100:.2f}%",
            "False Alarm Probability": f"{basic.false_alarm_probability * 100:.2f}%",
            "Interception Ratio": f"{events.interception_ratio * 100:.2f}%",
            "Average Intercept": f"{events.average_intercept_delay:.2f}",
            "Average Reward": f"{basic.average_reward:.3f}",
            "Coverage": f"{basic.coverage * 100:.2f}%",
        })
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

    render_section_header("SMART ADAPTIVE // KEY OUTCOMES", "Proposed strategy")
    kpis = st.columns(4)
    values = [
        ("Detection probability", f"{smart_basic.detection_probability * 100:.2f}%"),
        ("False alarm probability", f"{smart_basic.false_alarm_probability * 100:.2f}%"),
        ("Event interception", f"{smart_events.interception_ratio * 100:.2f}%"),
        ("Average reward", f"{smart_basic.average_reward:.3f}"),
    ]
    for column, (label, value) in zip(kpis, values):
        with column:
            render_kpi_card(label, value, accent=label == "Event interception")

    render_section_header("SPECTRUM ACTIVITY", f"{scenario.title()} scenario // {steps} time steps")
    spec_col, config_col = st.columns([2.4, 1], gap="large")
    with spec_col:
        st.pyplot(make_heatmap(environment, "Reference activity across time and frequency"), width="stretch")
        render_scan_pipeline()
    with config_col:
        render_run_configuration(scenario, bands, steps, seed, SimulatedReceiver(environment))

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

    render_section_header("SCHEDULER COMPARISON", "Lower visual weight for baselines")
    data = pd.DataFrame({
        "Strategy": STRATEGIES,
        "Detection Probability": [results[name]["basic"].detection_probability * 100 for name in STRATEGIES],
        "Interception Ratio": [results[name]["events"].interception_ratio * 100 for name in STRATEGIES],
    })
    chart_col, chart_col2 = st.columns(2, gap="large")
    with chart_col:
        st.pyplot(make_strategy_chart(data, "Detection Probability"), width="stretch")
    with chart_col2:
        st.pyplot(make_strategy_chart(data, "Interception Ratio"), width="stretch")

    render_section_header("BENCHMARK RESULTS", "One reproducible run // all values from runtime state")
    result_df = benchmark_table(results)
    styled = result_df.style.apply(lambda row: ["color:#e3262e;font-weight:600" if row["Strategy"] == "Smart Adaptive" else "" for _ in row], axis=1)
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

    render_section_header("SCAN ALLOCATION", "Where each strategy spent its scan opportunities")
    allocation_histories = get_scan_histories(scenario, bands, steps, seed)
    st.pyplot(make_allocation_chart(allocation_histories, bands), width="stretch")
    render_key_findings()
    render_methodology_table(scenario, bands, steps, seed)
