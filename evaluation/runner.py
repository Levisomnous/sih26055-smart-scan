from __future__ import annotations

from evaluation.metrics import EvaluationResult, calculate_metrics
from simulator.environment import SyntheticRFEnvironment
from simulator.receiver import SimulatedReceiver
from simulator.scan import ScanEngine


def run_scheduler_with_history(
    environment: SyntheticRFEnvironment,
    scheduler,
) -> tuple[EvaluationResult, list]:
    """
    Run a scheduler once through the simulated environment.

    Returns both:
    - calculated basic evaluation metrics
    - the exact scan history from that same simulation
    """

    receiver = SimulatedReceiver(environment)
    scan_engine = ScanEngine(receiver)

    for time_step in range(environment.num_steps):
        band = scheduler.select_band()

        observation = scan_engine.scan(
            time_step=time_step,
            band=band,
        )

        scheduler.update(observation)

    history = scan_engine.get_history()

    metrics = calculate_metrics(
        history=history,
        num_bands=environment.num_bands,
    )

    return metrics, history


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

    metrics, _ = run_scheduler_with_history(
        environment,
        scheduler,
    )

    return metrics
