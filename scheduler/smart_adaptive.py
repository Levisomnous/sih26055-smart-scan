from __future__ import annotations

import random
from collections import deque

from simulator.receiver import Observation

from .base import BaseScheduler


class SmartAdaptiveScheduler(BaseScheduler):
    """
    Balanced adaptive scheduler.

    The scheduler balances:

    1. Recent observed activity
    2. Uncertainty / limited observations
    3. Time since a band was last scanned

    It also maintains epsilon-greedy exploration.
    """

    ACTIVITY_WEIGHT = 0.60
    UNCERTAINTY_WEIGHT = 0.15
    AGE_WEIGHT = 0.25

    def __init__(
        self,
        num_bands: int,
        epsilon: float = 0.10,
        history_size: int = 8,
        seed: int = 42,
    ) -> None:
        super().__init__(num_bands)

        if not 0.0 <= epsilon <= 1.0:
            raise ValueError(
                "epsilon must be between 0 and 1"
            )

        if history_size <= 0:
            raise ValueError(
                "history_size must be greater than 0"
            )

        self.epsilon = epsilon
        self.history_size = history_size

        self.rng = random.Random(seed)

        self.histories = [
            deque(maxlen=history_size)
            for _ in range(num_bands)
        ]

        self.last_scanned = [-1] * num_bands

        self.current_time = 0

    def select_band(self) -> int:
        """
        Select the next band.

        A small probability is reserved for random exploration.
        Otherwise, select the band with the highest combined score.
        """

        # Explicit exploration.
        if self.rng.random() < self.epsilon:
            return self.rng.randrange(self.num_bands)

        # Initially give every band an opportunity to be observed.
        unobserved = [
            band
            for band in range(self.num_bands)
            if not self.histories[band]
        ]

        if unobserved:
            return self.rng.choice(unobserved)

        scores = self.get_band_scores()

        return max(
            range(self.num_bands),
            key=lambda band: scores[band],
        )

    def update(self, observation: Observation) -> None:
        """
        Store the latest observation and update scheduler state.
        """

        band = observation.band

        self.histories[band].append(
            int(observation.detected)
        )

        self.last_scanned[band] = observation.time_step

        self.current_time = observation.time_step

    def get_activity_scores(self) -> list[float]:
        """
        Estimate recent observed activity for each band.
        """

        scores = []

        for history in self.histories:
            if not history:
                scores.append(0.0)
            else:
                scores.append(
                    sum(history) / len(history)
                )

        return scores

    def get_uncertainty_scores(self) -> list[float]:
        """
        Higher score means the band has been observed less often.

        This encourages continued exploration of under-observed bands.
        """

        observation_counts = [
            len(history)
            for history in self.histories
        ]

        max_count = max(
            observation_counts,
            default=0,
        )

        if max_count == 0:
            return [1.0] * self.num_bands

        return [
            1.0 - (count / max_count)
            for count in observation_counts
        ]

    def get_age_scores(self) -> list[float]:
        """
        Estimate how overdue each band is for another observation.

        Recently scanned bands have low age scores.
        Bands not scanned for a long time have higher scores.
        """

        ages = []

        for last_time in self.last_scanned:
            if last_time < 0:
                ages.append(float(self.current_time + 1))
            else:
                ages.append(
                    float(self.current_time - last_time)
                )

        max_age = max(ages, default=1.0)

        if max_age <= 0:
            return [0.0] * self.num_bands

        return [
            age / max_age
            for age in ages
        ]

    def get_band_scores(self) -> list[float]:
        """
        Calculate the final scheduling score.

        We intentionally prioritize recent activity while still
        rewarding uncertainty and overdue observations.
        """

        activity = self.get_activity_scores()
        uncertainty = self.get_uncertainty_scores()
        age = self.get_age_scores()

        return [
            self._score_from_components(
                activity[band],
                uncertainty[band],
                age[band],
            )
            for band in range(self.num_bands)
        ]

    def _score_from_components(
        self,
        activity: float,
        uncertainty: float,
        age: float,
    ) -> float:
        return (
            self.ACTIVITY_WEIGHT * activity
            + self.UNCERTAINTY_WEIGHT * uncertainty
            + self.AGE_WEIGHT * age
        )

    def get_band_explanation(self, band: int) -> dict[str, float]:
        """Return the observable components behind one band's priority."""

        if not 0 <= band < self.num_bands:
            raise IndexError("band out of range")

        activity = self.get_activity_scores()[band]
        uncertainty = self.get_uncertainty_scores()[band]
        age = self.get_age_scores()[band]
        score = self._score_from_components(
            activity,
            uncertainty,
            age,
        )

        return {
            "activity": activity,
            "uncertainty": uncertainty,
            "age": age,
            "activity_contribution": self.ACTIVITY_WEIGHT * activity,
            "uncertainty_contribution": self.UNCERTAINTY_WEIGHT * uncertainty,
            "age_contribution": self.AGE_WEIGHT * age,
            "final_priority": score,
            "score": score,
        }