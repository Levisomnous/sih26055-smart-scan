from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.ui.benchmark_view import render_benchmark
from dashboard.ui.final_demo_view import render_final_demo
from dashboard.ui.live_view import render_live_demo
from dashboard.ui.theme import apply_theme
from simulator.environment import ScenarioConfig, SyntheticRFEnvironment

SCENARIOS = ["changing", "persistent", "periodic", "bursty", "mixed"]


def make_environment(scenario: str, bands: int, steps: int, seed: int) -> SyntheticRFEnvironment:
    return SyntheticRFEnvironment(ScenarioConfig(scenario, bands, steps, seed))


def sidebar_controls() -> tuple[str, str, int, int, int]:
    with st.sidebar:
        st.markdown('<div class="section-label">NAVIGATION</div>', unsafe_allow_html=True)
        mode = st.radio("Workspace", ["Benchmark", "Live Adaptive Demo", "Final Demo"], label_visibility="collapsed")
        st.markdown("---")
        st.markdown('<div class="section-label sidebar-controls-label">SIMULATION CONTROLS</div>', unsafe_allow_html=True)
        scenario = st.selectbox("Scenario", SCENARIOS, index=0)
        bands = st.slider("Frequency bands", 10, 30, 20)
        steps = st.slider("Time steps", 50, 300, 100)
        seed = int(st.number_input("Random seed", min_value=0, value=42, step=1))
        st.markdown("---")
        st.markdown('<div class="mono-label"><span class="synthetic-dot">●</span> SYNTHETIC ONLY<br>REPRODUCIBLE RUNS</div>', unsafe_allow_html=True)
    return mode, scenario, bands, steps, seed


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
        render_live_demo(environment, scenario, bands, steps, seed)
    else:
        render_final_demo()


if __name__ == "__main__":
    main()