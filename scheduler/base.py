from __future__ import annotations

from abc import ABC, abstractmethod

from simulator.receiver import Observation


class BaseScheduler(ABC):
    """
    Common interface for all scan-scheduling strategies.
    """

    def __init__(self, num_bands: int) -> None:
        if num_bands <= 0:
            raise ValueError("num_bands must be greater than 0")

        self.num_bands = num_bands

    @abstractmethod
    def select_band(self) -> int:
        """
        Select the next frequency band to observe.

        Returns:
            Band index in the range [0, num_bands - 1].
        """
        raise NotImplementedError

    def update(self, observation: Observation) -> None:
        """
        Receive feedback from the latest observation.

        Basic schedulers do not need feedback, so the default
        implementation does nothing.
        """
        return