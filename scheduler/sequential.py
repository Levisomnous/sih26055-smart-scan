from __future__ import annotations

from .base import BaseScheduler


class SequentialScheduler(BaseScheduler):
    """
    Baseline scheduler.

    Cycles through frequency bands in order:

    B1 → B2 → B3 → ... → B20 → B1 → ...
    """

    def __init__(self, num_bands: int) -> None:
        super().__init__(num_bands)
        self.current_band = 0

    def select_band(self) -> int:
        band = self.current_band

        self.current_band = (
            self.current_band + 1
        ) % self.num_bands

        return band