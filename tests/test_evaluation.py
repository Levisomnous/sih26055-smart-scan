from evaluation.benchmark import run_benchmark
from evaluation.event_metrics import (
    evaluate_interception,
    find_activity_events,
)
from evaluation.runner import run_scheduler_with_history
from scheduler.sequential import SequentialScheduler
from simulator.environment import ScenarioConfig, SyntheticRFEnvironment


def test_scheduler_run_produces_expected_number_of_scans():
    environment = SyntheticRFEnvironment(
        ScenarioConfig(
            name="changing",
            num_bands=20,
            num_steps=25,
            seed=42,
        )
    )

    scheduler = SequentialScheduler(20)

    metrics, history = run_scheduler_with_history(
        environment,
        scheduler,
    )

    assert len(history) == 25
    assert metrics.total_scans == 25


def test_basic_metrics_have_valid_ranges():
    environment = SyntheticRFEnvironment(
        ScenarioConfig(
            name="changing",
            num_bands=20,
            num_steps=30,
            seed=42,
        )
    )

    scheduler = SequentialScheduler(20)

    metrics, _ = run_scheduler_with_history(
        environment,
        scheduler,
    )

    assert 0.0 <= metrics.detection_probability <= 1.0
    assert 0.0 <= metrics.false_alarm_probability <= 1.0
    assert 0.0 <= metrics.coverage <= 1.0


def test_event_count_matches_environment():
    environment = SyntheticRFEnvironment(
        ScenarioConfig(
            name="changing",
            num_bands=20,
            num_steps=100,
            seed=42,
        )
    )

    events = find_activity_events(environment)

    assert len(events) > 0

    for time_step, band in events:
        assert 0 <= time_step < environment.num_steps
        assert 0 <= band < environment.num_bands


def test_event_metrics_are_consistent():
    environment = SyntheticRFEnvironment(
        ScenarioConfig(
            name="changing",
            num_bands=20,
            num_steps=100,
            seed=42,
        )
    )

    scheduler = SequentialScheduler(20)

    _, history = run_scheduler_with_history(
        environment,
        scheduler,
    )

    result = evaluate_interception(
        environment,
        history,
    )

    assert result.total_events >= 0
    assert result.intercepted_events >= 0
    assert result.missed_events >= 0

    assert (
        result.intercepted_events
        + result.missed_events
        == result.total_events
    )

    assert 0.0 <= result.interception_ratio <= 1.0

    assert result.average_intercept_delay >= 0.0
    assert result.max_intercept_delay >= 0


def test_benchmark_runs_all_default_strategies():
    results = run_benchmark(
        scenario_name="changing",
        num_bands=20,
        num_steps=30,
        seed=42,
    )

    expected = {
        "Sequential",
        "Random",
        "Adaptive",
        "Smart Adaptive",
    }

    assert set(results.keys()) == expected

    for result in results.values():
        assert "basic" in result
        assert "events" in result


def test_benchmark_is_reproducible():
    first = run_benchmark(
        scenario_name="changing",
        num_bands=20,
        num_steps=50,
        seed=42,
    )

    second = run_benchmark(
        scenario_name="changing",
        num_bands=20,
        num_steps=50,
        seed=42,
    )

    assert first == second
