from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.demo_runner import DemoRunner
from evaluation.benchmark import run_benchmark
from simulator.environment import (
    ScenarioConfig,
    SyntheticRFEnvironment,
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="SIH26055 Smart Scan Strategy",
    layout="wide",
)


# =========================================================
# TITLE
# =========================================================

st.title("SIH26055 — Smart Scan Strategy")

st.caption(
    "Synthetic academic simulation of adaptive scan scheduling"
)


# =========================================================
# SESSION STATE
# =========================================================

if "demo_runner" not in st.session_state:
    st.session_state.demo_runner = None

if "demo_state" not in st.session_state:
    st.session_state.demo_state = None

if "benchmark_results" not in st.session_state:
    st.session_state.benchmark_results = None


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("Simulation Controls")

mode = st.sidebar.radio(
    "Mode",
    [
        "Benchmark",
        "Live Adaptive Demo",
    ],
)

scenario = st.sidebar.selectbox(
    "Scenario",
    [
        "changing",
        "persistent",
        "periodic",
        "bursty",
        "mixed",
    ],
    index=0,
)

num_bands = st.sidebar.slider(
    "Frequency bands",
    min_value=10,
    max_value=30,
    value=20,
)

num_steps = st.sidebar.slider(
    "Time steps",
    min_value=50,
    max_value=300,
    value=100,
)

seed = st.sidebar.number_input(
    "Random seed",
    min_value=0,
    value=42,
    step=1,
)


# =========================================================
# ENVIRONMENT
# =========================================================

config = ScenarioConfig(
    name=scenario,
    num_bands=num_bands,
    num_steps=num_steps,
    seed=int(seed),
)

environment = SyntheticRFEnvironment(config)


# =========================================================
# GROUND TRUTH VISUALIZATION
# =========================================================

st.subheader("Simulated Frequency × Time Environment")

fig, ax = plt.subplots(figsize=(14, 5))

ax.imshow(
    environment.activity.T,
    aspect="auto",
    interpolation="nearest",
)

ax.set_xlabel("Time Step")
ax.set_ylabel("Frequency Band")

ax.set_title(
    f"Simulator Ground Truth — {scenario.title()} Scenario"
)

ax.set_yticks(range(num_bands))

ax.set_yticklabels(
    [f"B{i + 1}" for i in range(num_bands)]
)

st.pyplot(fig)

plt.close(fig)


# =========================================================
# BENCHMARK MODE
# =========================================================

if mode == "Benchmark":

    st.subheader("Benchmark Comparison")

    run_button = st.sidebar.button(
        "Run Benchmark",
        type="primary",
    )

    if (
        run_button
        or st.session_state.benchmark_results is None
    ):

        with st.spinner("Running benchmark..."):

            st.session_state.benchmark_results = (
                run_benchmark(
                    scenario_name=scenario,
                    num_bands=num_bands,
                    num_steps=num_steps,
                    seed=int(seed),
                )
            )

    results = st.session_state.benchmark_results

    rows = []

    for name, result in results.items():

        basic = result["basic"]
        events = result["events"]

        rows.append(
            {
                "Strategy": name,
                "Detection Probability":
                    basic.detection_probability,
                "False Alarm Probability":
                    basic.false_alarm_probability,
                "Interception Ratio":
                    events.interception_ratio,
                "Average Intercept":
                    events.average_intercept_delay,
                "Average Reward":
                    basic.average_reward,
                "Coverage":
                    basic.coverage,
            }
        )

    df = pd.DataFrame(rows)

    display_df = df.copy()

    for column in [
        "Detection Probability",
        "False Alarm Probability",
        "Interception Ratio",
        "Coverage",
    ]:
        display_df[column] = (
            display_df[column] * 100
        ).round(2).astype(str) + "%"

    display_df["Average Intercept"] = (
        display_df["Average Intercept"].round(2)
    )

    display_df["Average Reward"] = (
        display_df["Average Reward"].round(3)
    )

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
    )

    # -----------------------------------------------------
    # General benchmark charts
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Detection Probability")

        detection_chart = df.set_index(
            "Strategy"
        )[["Detection Probability"]]

        st.bar_chart(detection_chart)

    with col2:

        st.subheader("Interception Ratio")

        interception_chart = df.set_index(
            "Strategy"
        )[["Interception Ratio"]]

        st.bar_chart(interception_chart)

    st.subheader("Average Intercept Delay")

    delay_chart = df.set_index(
        "Strategy"
    )[["Average Intercept"]]

    st.bar_chart(delay_chart)

    # -----------------------------------------------------
    # Conventional vs Smart Adaptive
    # -----------------------------------------------------

    st.divider()

    st.subheader("Conventional vs Smart Adaptive")

    sequential = results["Sequential"]
    smart = results["Smart Adaptive"]

    seq_basic = sequential["basic"]
    seq_events = sequential["events"]

    smart_basic = smart["basic"]
    smart_events = smart["events"]

    comparison_rows = [
        {
            "Metric": "Detection Probability",
            "Sequential": seq_basic.detection_probability,
            "Smart Adaptive": smart_basic.detection_probability,
        },
        {
            "Metric": "False Alarm Probability",
            "Sequential": seq_basic.false_alarm_probability,
            "Smart Adaptive": smart_basic.false_alarm_probability,
        },
        {
            "Metric": "Interception Ratio",
            "Sequential": seq_events.interception_ratio,
            "Smart Adaptive": smart_events.interception_ratio,
        },
        {
            "Metric": "Average Intercept Delay",
            "Sequential": seq_events.average_intercept_delay,
            "Smart Adaptive": smart_events.average_intercept_delay,
        },
        {
            "Metric": "Average Reward",
            "Sequential": seq_basic.average_reward,
            "Smart Adaptive": smart_basic.average_reward,
        },
    ]

    comparison_df = pd.DataFrame(comparison_rows)

    # Create a separate display dataframe so that the original
    # numerical dataframe remains untouched.
    display_comparison = comparison_df.astype(
        {
            "Metric": "string",
            "Sequential": "object",
            "Smart Adaptive": "object",
        }
    ).copy()

    # Format percentage metrics.
    percentage_metrics = {
        "Detection Probability",
        "False Alarm Probability",
        "Interception Ratio",
    }

    for row_index, row in comparison_df.iterrows():

        metric = row["Metric"]

        if metric in percentage_metrics:

            display_comparison.at[
                row_index,
                "Sequential"
            ] = f"{row['Sequential'] * 100:.2f}%"

            display_comparison.at[
                row_index,
                "Smart Adaptive"
            ] = f"{row['Smart Adaptive'] * 100:.2f}%"

        elif metric == "Average Intercept Delay":

            display_comparison.at[
                row_index,
                "Sequential"
            ] = f"{row['Sequential']:.2f}"

            display_comparison.at[
                row_index,
                "Smart Adaptive"
            ] = f"{row['Smart Adaptive']:.2f}"

        elif metric == "Average Reward":

            display_comparison.at[
                row_index,
                "Sequential"
            ] = f"{row['Sequential']:.3f}"

            display_comparison.at[
                row_index,
                "Smart Adaptive"
            ] = f"{row['Smart Adaptive']:.3f}"

    st.dataframe(
        display_comparison,
        width="stretch",
        hide_index=True,
    )

    # -----------------------------------------------------
    # Focused comparison charts
    # -----------------------------------------------------

       # -----------------------------------------------------
    # CLEAR SIDE-BY-SIDE COMPARISON CHARTS
    # -----------------------------------------------------

    st.subheader("Detection Probability")

    detection_chart_df = pd.DataFrame(
        {
            "Strategy": [
                "Sequential",
                "Smart Adaptive",
            ],
            "Detection Probability": [
                seq_basic.detection_probability * 100,
                smart_basic.detection_probability * 100,
            ],
        }
    )

    st.bar_chart(
        detection_chart_df,
        x="Strategy",
        y="Detection Probability",
    )

    st.subheader("Interception Ratio")

    interception_chart_df = pd.DataFrame(
        {
            "Strategy": [
                "Sequential",
                "Smart Adaptive",
            ],
            "Interception Ratio": [
                seq_events.interception_ratio * 100,
                smart_events.interception_ratio * 100,
            ],
        }
    )

    st.bar_chart(
        interception_chart_df,
        x="Strategy",
        y="Interception Ratio",
    )

# =========================================================
# LIVE DEMO MODE
# =========================================================

else:

    st.subheader("Live Adaptive Scheduler")

    st.info(
        "The scheduler chooses one band at a time, receives "
        "the simulated observation, and updates its priorities."
    )

    # -----------------------------------------------------
    # Reset button
    # -----------------------------------------------------

    if st.sidebar.button("Reset Live Demo"):

        st.session_state.demo_runner = DemoRunner(
            environment=environment,
            seed=int(seed),
        )

        st.session_state.demo_state = None

        st.rerun()

    # -----------------------------------------------------
    # Initialize runner
    # -----------------------------------------------------

    if (
        st.session_state.demo_runner is None
        or (
            st.session_state.demo_runner.environment.seed
            != environment.seed
        )
        or (
            st.session_state.demo_runner.environment.config.name
            != environment.config.name
        )
        or (
            st.session_state.demo_runner.environment.num_steps
            != environment.num_steps
        )
        or (
            st.session_state.demo_runner.environment.num_bands
            != environment.num_bands
        )
    ):

        st.session_state.demo_runner = DemoRunner(
            environment=environment,
            seed=int(seed),
        )

        st.session_state.demo_state = None

    runner = st.session_state.demo_runner

    # -----------------------------------------------------
    # Buttons
    # -----------------------------------------------------

    col_button1, col_button2 = st.columns(2)

    with col_button1:

        next_scan = st.button(
            "▶ Next Scan",
            type="primary",
            width="stretch",
        )

    with col_button2:

        run_all = st.button(
            "▶ Run Full Demo",
            width="stretch",
        )

    # -----------------------------------------------------
    # Execute one step
    # -----------------------------------------------------

    if next_scan:

        st.session_state.demo_state = (
            runner.step()
        )

    # -----------------------------------------------------
    # Execute entire demo
    # -----------------------------------------------------

    if run_all:

        while not runner.state.finished:
            st.session_state.demo_state = (
                runner.step()
            )

    state = st.session_state.demo_state

    # -----------------------------------------------------
    # CURRENT STATE
    # -----------------------------------------------------

    st.subheader("Current Scheduler State")

    if state is None:

        st.write(
            "Press **Next Scan** to begin the simulation."
        )

    else:

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Time Step",
                state.time_step,
            )

        with col2:

            st.metric(
                "Selected Band",
                f"B{state.selected_band + 1}",
            )

        with col3:

            result_text = (
                "DETECTED"
                if state.detected
                else "NOT DETECTED"
            )

            st.metric(
                "Observation",
                result_text,
            )

        with col4:

            st.metric(
                "Reward",
                f"{state.reward:+.1f}",
            )

    # -----------------------------------------------------
    # BAND PRIORITIES
    # -----------------------------------------------------

    st.subheader("Current Band Priorities")

    scores = runner.get_scores()

    if state is not None and state.selected_band is not None:

        selected_band = state.selected_band
        selected_score = scores[selected_band]

        st.info(
            f"Scheduler selected **B{selected_band + 1}** "
            f"with current priority score "
            f"**{selected_score:.2f}**."
        )

    score_df = pd.DataFrame(
        {
            "Band": [
                f"B{i + 1}"
                for i in range(len(scores))
            ],
            "Priority": scores,
        }
    )

    score_df = score_df.sort_values(
        "Priority",
        ascending=False,
    )

    st.bar_chart(
        score_df.set_index("Band")
    )

    # -----------------------------------------------------
    # SCAN PATH
    # -----------------------------------------------------

    history = runner.get_history()

    if history:

        st.subheader("Live Scan Path")

        path_df = pd.DataFrame(
            {
                "Time": [
                    record.time_step
                    for record in history
                ],
                "Band": [
                    record.band + 1
                    for record in history
                ],
            }
        )

        st.line_chart(
            path_df.set_index("Time"),
            y="Band",
        )

    # -----------------------------------------------------
    # SCAN HISTORY
    # -----------------------------------------------------

    if history:

        st.subheader("Recent Scan History")

        history_rows = []

        for record in history[-10:]:

            history_rows.append(
                {
                    "Time": record.time_step,
                    "Band": f"B{record.band + 1}",
                    "Truth Active":
                        "Yes"
                        if record.truth_active
                        else "No",
                    "Detected":
                        "Yes"
                        if record.detected
                        else "No",
                    "False Alarm":
                        "Yes"
                        if record.false_alarm
                        else "No",
                }
            )

        st.dataframe(
            pd.DataFrame(history_rows),
            width="stretch",
            hide_index=True,
        )

    # -----------------------------------------------------
    # LIVE STATUS
    # -----------------------------------------------------

    if runner.state.finished:

        st.success(
            "Simulation complete."
        )

    else:

        st.caption(
            f"Next decision available at "
            f"time step {runner.time_step}."
        )


# =========================================================
# EXPLANATION
# =========================================================

st.divider()

st.subheader("How the Prototype Works")

st.markdown(
    """
**1. Simulate** — Generate synthetic activity across
frequency bands and time.

**2. Observe** — A simulated receiver observes a limited
portion of the environment.

**3. Decide** — The adaptive scheduler selects the next
band using previous observations.

**4. Learn** — HIT/MISS feedback updates the scheduler's
estimated priorities.

**5. Evaluate** — The proposed strategy is compared with
conventional baselines.
"""
)