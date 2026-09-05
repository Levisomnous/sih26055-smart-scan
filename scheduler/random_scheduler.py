from __future__ import annotations

import random

from .base import BaseScheduler


class RandomScheduler(BaseScheduler):
    """
    Baseline scheduler that randomly selects
    a frequency band at every time step.
    """

    def __init__(self, num_bands: int, seed: int = 42) -> None:
        super().__init__(num_bands)

        self.rng = random.Random(seed)

    def select_band(self) -> int:
        return self.rng.randrange(self.num_bands)