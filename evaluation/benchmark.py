from __future__ import annotations

from typing import Callable

from evaluation.event_metrics import evaluate_interception
from evaluation.runner import run_scheduler_with_history

from scheduler.adaptive import AdaptiveScheduler
from scheduler.random_scheduler import RandomScheduler
from scheduler.sequential import SequentialScheduler
from scheduler.smart_adaptive import SmartAdaptiveScheduler

from simulator.environment import (
    ScenarioConfig,
    SyntheticRFEnvironment,
)


SchedulerFactory = Callable[[], object]


def default_scheduler_factories(
    num_bands: int,
    seed: int,
) -> dict[str, SchedulerFactory]:
    """
    Return the standard four benchmark strategies.
    """

    return {
        "Sequential": lambda: SequentialScheduler(
            num_bands
        ),

        "Random": lambda: RandomScheduler(
            num_bands,
            seed=seed,
        ),

        "Adaptive": lambda: AdaptiveScheduler(
            num_bands,
            epsilon=0.15,
            seed=seed,
        ),

        "Smart Adaptive": lambda: SmartAdaptiveScheduler(
            num_bands,
            epsilon=0.15,
            history_size=10,
            seed=seed,
        ),
    }


def run_benchmark(
    scenario_name: str = "changing",
    num_bands: int = 20,
    num_steps: int = 100,
    seed: int = 42,
    scheduler_factories: dict[str, SchedulerFactory] | None = None,
) -> dict[str, dict]:
    """
    Run all supplied schedulers on identical simulated environments.

    Each strategy is simulated exactly once.

    Basic metrics and event-level metrics are calculated from
    the exact same scan history.

    If scheduler_factories is omitted, the standard four
    benchmark strategies are used.
    """

    if scheduler_factories is None:
        scheduler_factories = default_scheduler_factories(
            num_bands=num_bands,
            seed=seed,
        )

    results: dict[str, dict] = {}

    for name, create_scheduler in scheduler_factories.items():

        config = ScenarioConfig(
            name=scenario_name,
            num_bands=num_bands,
            num_steps=num_steps,
            seed=seed,
        )

        environment = SyntheticRFEnvironment(config)

        scheduler = create_scheduler()

        # ONE simulation run.
        basic_result, history = run_scheduler_with_history(
            environment,
            scheduler,
        )

        # Calculate event metrics from the exact same history.
        event_result = evaluate_interception(
            environment,
            history,
        )

        results[name] = {
            "basic": basic_result,
            "events": event_result,
        }

    return results
