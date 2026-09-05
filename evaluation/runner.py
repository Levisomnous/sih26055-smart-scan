from __future__ import annotations

from evaluation.metrics import EvaluationResult, calculate_metrics
from simulator.environment import SyntheticRFEnvironment
from simulator.receiver import SimulatedReceiver
from simulator.scan import ScanEngine


def run_scheduler(
    environment: SyntheticRFEnvironment,
    scheduler,
) -> EvaluationResult:
    """
    Run a scheduler through the simulated environment.

    The scheduler chooses a band.
    The receiver observes it.
    The scheduler receives the observation as feedback.
    """

    receiver = SimulatedReceiver(environment)
    scan_engine = ScanEngine(receiver)

    for time_step in range(environment.num_steps):
        band = scheduler.select_band()

        observation = scan_engine.scan(
            time_step=time_step,
            band=band,
        )

        # Give the scheduler the observation it just received.
        scheduler.update(observation)

    return calculate_metrics(
        history=scan_engine.get_history(),
        num_bands=environment.num_bands,
    )