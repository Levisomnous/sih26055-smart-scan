from __future__ import annotations

from dataclasses import dataclass

from .environment import SyntheticRFEnvironment


@dataclass
class Observation:
    """
    Result of one simulated receiver observation.
    """

    time_step: int
    band: int

    # Hidden truth, used by evaluation only.
    truth_active: bool

    # What the receiver actually reported.
    detected: bool

    @property
    def false_alarm(self) -> bool:
        """
        True when the receiver reports activity even though
        the simulated truth says the band is inactive.
        """
        return self.detected and not self.truth_active


class SimulatedReceiver:
    """
    Receiver model with configurable detection and false-alarm
    probabilities.

    This remains a synthetic academic simulation.
    """

    def __init__(
        self,
        environment: SyntheticRFEnvironment,
        detection_probability: float = 0.90,
        false_alarm_probability: float = 0.05,
        seed: int = 123,
    ) -> None:

        if not 0.0 <= detection_probability <= 1.0:
            raise ValueError(
                "detection_probability must be between 0 and 1"
            )

        if not 0.0 <= false_alarm_probability <= 1.0:
            raise ValueError(
                "false_alarm_probability must be between 0 and 1"
            )

        self.environment = environment

        self.detection_probability = detection_probability
        self.false_alarm_probability = false_alarm_probability

        # Use a separate random generator so receiver noise
        # does not modify the environment itself.
        import numpy as np

        self.rng = np.random.default_rng(seed)

    def observe(
        self,
        time_step: int,
        band: int,
    ) -> Observation:

        if not 0 <= time_step < self.environment.num_steps:
            raise IndexError("time_step out of range")

        if not 0 <= band < self.environment.num_bands:
            raise IndexError("band out of range")

        truth = bool(
            self.environment.get_truth(
                time_step,
                band,
            )
        )

        if truth:
            detected = (
                self.rng.random()
                < self.detection_probability
            )
        else:
            detected = (
                self.rng.random()
                < self.false_alarm_probability
            )

        return Observation(
            time_step=time_step,
            band=band,
            truth_active=truth,
            detected=bool(detected),
        )