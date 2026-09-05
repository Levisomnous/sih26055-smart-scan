from __future__ import annotations

import random

from simulator.receiver import Observation

from .base import BaseScheduler


class AdaptiveScheduler(BaseScheduler):
    """
    Simple adaptive activity-based scheduler.

    The scheduler estimates how useful each band has been based
    on observed hits and misses.

    It uses epsilon-greedy selection:

        With probability epsilon:
            explore a random band.

        Otherwise:
            exploit the band with the highest estimated activity.
    """

    def __init__(
        self,
        num_bands: int,
        epsilon: float = 0.15,
        seed: int = 42,
    ) -> None:
        super().__init__(num_bands)

        if not 0.0 <= epsilon <= 1.0:
            raise ValueError("epsilon must be between 0 and 1")

        self.epsilon = epsilon
        self.rng = random.Random(seed)

        # Number of observations for each band.
        self.observation_counts = [0] * num_bands

        # Number of hits observed for each band.
        self.hit_counts = [0] * num_bands

    def select_band(self) -> int:
        """
        Select the next band using epsilon-greedy exploration.
        """

        # Exploration
        if self.rng.random() < self.epsilon:
            return self.rng.randrange(self.num_bands)

        # If some bands have never been observed, explore them first.
        unobserved_bands = [
            band
            for band in range(self.num_bands)
            if self.observation_counts[band] == 0
        ]

        if unobserved_bands:
            return self.rng.choice(unobserved_bands)

        # Exploitation:
        # choose the band with the highest observed hit rate.
        hit_rates = [
            self.hit_counts[band]
            / self.observation_counts[band]
            for band in range(self.num_bands)
        ]

        return max(
            range(self.num_bands),
            key=lambda band: hit_rates[band],
        )

    def update(self, observation: Observation) -> None:
        """
        Update the scheduler's knowledge after an observation.
        """

        band = observation.band

        self.observation_counts[band] += 1

        if observation.detected:
          self.hit_counts[band] += 1

    def get_band_scores(self) -> list[float]:
        """
        Return the current estimated hit rate for each band.
        """

        scores = []

        for band in range(self.num_bands):
            observations = self.observation_counts[band]

            if observations == 0:
                scores.append(0.0)
            else:
                scores.append(
                    self.hit_counts[band] / observations
                )

        return scores