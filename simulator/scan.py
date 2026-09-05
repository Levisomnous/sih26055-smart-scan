from __future__ import annotations

from dataclasses import dataclass

from .receiver import Observation, SimulatedReceiver


@dataclass
class ScanRecord:
    time_step: int
    band: int

    truth_active: bool
    detected: bool

    @property
    def true_detection(self) -> bool:
        return self.truth_active and self.detected

    @property
    def false_alarm(self) -> bool:
        return not self.truth_active and self.detected


class ScanEngine:
    """
    Controls interaction between scheduler and receiver.
    """

    def __init__(self, receiver: SimulatedReceiver) -> None:
        self.receiver = receiver
        self.history: list[ScanRecord] = []

    def scan(
        self,
        time_step: int,
        band: int,
    ) -> Observation:

        observation = self.receiver.observe(
            time_step,
            band,
        )

        record = ScanRecord(
            time_step=observation.time_step,
            band=observation.band,
            truth_active=observation.truth_active,
            detected=observation.detected,
        )

        self.history.append(record)

        return observation

    def get_history(self) -> list[ScanRecord]:
        return self.history.copy()