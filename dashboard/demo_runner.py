from __future__ import annotations

from dataclasses import dataclass

from simulator.environment import SyntheticRFEnvironment
from simulator.receiver import SimulatedReceiver
from simulator.scan import ScanEngine
from scheduler.smart_adaptive import SmartAdaptiveScheduler


@dataclass
class DemoState:
    time_step: int
    selected_band: int | None
    detected: bool | None
    reward: float
    finished: bool


class DemoRunner:
    """
    Controls one live run of the Smart Adaptive Scheduler.
    """

    def __init__(
        self,
        environment: SyntheticRFEnvironment,
        epsilon: float = 0.10,
        history_size: int = 8,
        receiver_detection_probability: float = 0.90,
        receiver_false_alarm_probability: float = 0.05,
        seed: int = 42,
    ) -> None:

        self.environment = environment

        self.receiver = SimulatedReceiver(
            environment,
            detection_probability=receiver_detection_probability,
            false_alarm_probability=receiver_false_alarm_probability,
            seed=seed + 100,
        )

        self.scan_engine = ScanEngine(
            self.receiver
        )

        self.scheduler = SmartAdaptiveScheduler(
            num_bands=environment.num_bands,
            epsilon=epsilon,
            history_size=history_size,
            seed=seed,
        )

        self.time_step = 0

        self.state = DemoState(
            time_step=0,
            selected_band=None,
            detected=None,
            reward=0.0,
            finished=False,
        )

    def step(self) -> DemoState:
        """
        Execute exactly one scheduler decision.
        """

        if self.time_step >= self.environment.num_steps:
            self.state.finished = True
            return self.state

        band = self.scheduler.select_band()

        observation = self.scan_engine.scan(
            time_step=self.time_step,
            band=band,
        )

        self.scheduler.update(observation)

        # Keep live-demo reward consistent with evaluation.metrics:
        # true detection = +1
        # false alarm    = -1
        # miss/correct negative = 0
        if observation.truth_active and observation.detected:
            reward = 1.0
        elif not observation.truth_active and observation.detected:
            reward = -1.0
        else:
            reward = 0.0

        self.state = DemoState(
            time_step=self.time_step,
            selected_band=band,
            detected=observation.detected,
            reward=reward,
            finished=False,
        )

        self.time_step += 1

        if self.time_step >= self.environment.num_steps:
            self.state.finished = True

        return self.state

    def get_scores(self) -> list[float]:
        """
        Return current scheduler scores for every band.
        """
        return self.scheduler.get_band_scores()

    def get_history(self):
        """
        Return the scan history.
        """
        return self.scan_engine.get_history()