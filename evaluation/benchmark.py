from __future__ import annotations

from typing import Callable

from evaluation.event_metrics import evaluate_interception
from evaluation.runner import run_scheduler

from scheduler.adaptive import AdaptiveScheduler
from scheduler.random_scheduler import RandomScheduler
from scheduler.sequential import SequentialScheduler
from scheduler.smart_adaptive import SmartAdaptiveScheduler

from simulator.environment import (
    ScenarioConfig,
    SyntheticRFEnvironment,
)


def run_benchmark(
    scenario_name: str = "changing",
    num_bands: int = 20,
    num_steps: int = 100,
    seed: int = 42,
) -> dict[str, dict]:
    """
    Run all schedulers on the same simulated environment.
    """

    scheduler_factories: dict[str, Callable] = {
        "Sequential": lambda: SequentialScheduler(num_bands),

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

    results = {}

    for name, create_scheduler in scheduler_factories.items():

        config = ScenarioConfig(
            name=scenario_name,
            num_bands=num_bands,
            num_steps=num_steps,
            seed=seed,
        )

        environment = SyntheticRFEnvironment(config)

        scheduler = create_scheduler()

        basic_result = run_scheduler(
            environment,
            scheduler,
        )

        # We need access to the scan history, so run the
        # scheduler again through a small local loop.
        from simulator.receiver import SimulatedReceiver
        from simulator.scan import ScanEngine

        receiver = SimulatedReceiver(environment)
        scan_engine = ScanEngine(receiver)

        scheduler = create_scheduler()

        for time_step in range(environment.num_steps):
            band = scheduler.select_band()

            observation = scan_engine.scan(
                time_step=time_step,
                band=band,
            )

            scheduler.update(observation)

        event_result = evaluate_interception(
            environment,
            scan_engine.get_history(),
        )

        results[name] = {
            "basic": basic_result,
            "events": event_result,
        }

    return results