from simulator.environment import ScenarioConfig, SyntheticRFEnvironment
from simulator.receiver import Observation
from dashboard.demo_runner import DemoRunner
from scheduler.smart_adaptive import SmartAdaptiveScheduler


def test_demo_runner_steps():
    config = ScenarioConfig(
        name="changing",
        num_bands=20,
        num_steps=10,
        seed=42,
    )

    environment = SyntheticRFEnvironment(config)

    runner = DemoRunner(
        environment=environment,
        seed=42,
    )

    state = runner.step()

    assert 0 <= state.selected_band < 20
    assert state.time_step == 0
    assert state.reward in (-1.0, 0.0, 1.0)


def test_smart_scheduler_selects_valid_bands():
    scheduler = SmartAdaptiveScheduler(
        num_bands=20,
        epsilon=0.1,
        history_size=8,
        seed=42,
    )

    for _ in range(50):
        band = scheduler.select_band()
        assert 0 <= band < 20

        scheduler.update(
            Observation(
                time_step=scheduler.current_time,
                band=band,
                truth_active=False,
                detected=False,
            )
        )


def test_scheduler_update_changes_state():
    scheduler = SmartAdaptiveScheduler(
        num_bands=5,
        epsilon=0.0,
        history_size=4,
        seed=42,
    )

    observation = Observation(
        time_step=7,
        band=2,
        truth_active=True,
        detected=True,
    )

    scheduler.update(observation)

    assert list(scheduler.histories[2]) == [1]
    assert scheduler.last_scanned[2] == 7
    assert scheduler.current_time == 7


def test_activity_score_tracks_recent_detections():
    scheduler = SmartAdaptiveScheduler(
        num_bands=3,
        epsilon=0.0,
        history_size=4,
        seed=42,
    )

    scheduler.update(
        Observation(
            time_step=0,
            band=1,
            truth_active=True,
            detected=True,
        )
    )

    scheduler.update(
        Observation(
            time_step=1,
            band=1,
            truth_active=False,
            detected=False,
        )
    )

    scores = scheduler.get_activity_scores()

    assert scores[1] == 0.5
    assert scores[0] == 0.0
    assert scores[2] == 0.0


def test_scores_are_valid():
    scheduler = SmartAdaptiveScheduler(
        num_bands=5,
        epsilon=0.0,
        history_size=4,
        seed=42,
    )

    scheduler.update(
        Observation(
            time_step=3,
            band=2,
            truth_active=True,
            detected=True,
        )
    )

    scores = scheduler.get_band_scores()

    assert len(scores) == 5
    assert all(score >= 0.0 for score in scores)


def test_scheduler_is_reproducible_with_same_seed():
    scheduler_a = SmartAdaptiveScheduler(
        num_bands=10,
        epsilon=0.15,
        history_size=8,
        seed=123,
    )

    scheduler_b = SmartAdaptiveScheduler(
        num_bands=10,
        epsilon=0.15,
        history_size=8,
        seed=123,
    )

    sequence_a = []
    sequence_b = []

    for time_step in range(20):
        band_a = scheduler_a.select_band()
        band_b = scheduler_b.select_band()

        sequence_a.append(band_a)
        sequence_b.append(band_b)

        observation_a = Observation(
            time_step=time_step,
            band=band_a,
            truth_active=False,
            detected=False,
        )

        observation_b = Observation(
            time_step=time_step,
            band=band_b,
            truth_active=False,
            detected=False,
        )

        scheduler_a.update(observation_a)
        scheduler_b.update(observation_b)

    assert sequence_a == sequence_b
