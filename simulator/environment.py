from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class ScenarioConfig:
    """
    Configuration describing one synthetic environment scenario.
    """

    name: str
    num_bands: int = 20
    num_steps: int = 100
    seed: int = 42


class SyntheticRFEnvironment:
    """
    Safe academic simulation of activity across frequency bands and time.

    The simulator contains hidden ground truth.

    The scheduler must never access the ground truth directly.
    """

    def __init__(self, config: ScenarioConfig) -> None:
        self.config = config

        if config.num_bands <= 0:
            raise ValueError("num_bands must be greater than 0")

        if config.num_steps <= 0:
            raise ValueError("num_steps must be greater than 0")

        self.num_bands = config.num_bands
        self.num_steps = config.num_steps
        self.seed = config.seed

        self.rng = np.random.default_rng(config.seed)

        self.activity = self._generate_activity(config.name)

    def _generate_activity(self, scenario: str) -> np.ndarray:
        """
        Generate synthetic frequency/time activity.
        """

        scenario = scenario.lower().strip()

        activity = np.zeros(
            (self.num_steps, self.num_bands),
            dtype=np.int8,
        )

        if scenario == "persistent":
            return self._persistent_scenario(activity)

        if scenario == "periodic":
            return self._periodic_scenario(activity)

        if scenario == "bursty":
            return self._bursty_scenario(activity)

        if scenario == "changing":
            return self._changing_scenario(activity)

        if scenario == "mixed":
            return self._mixed_scenario(activity)

        raise ValueError(
            f"Unknown scenario: {scenario}. "
            f"Choose persistent, periodic, bursty, changing, or mixed."
        )

    def _persistent_scenario(
        self,
        activity: np.ndarray,
    ) -> np.ndarray:
        """
        A few bands have consistently higher activity.
        """

        high_activity_bands = [2, 6, 14]

        for band in high_activity_bands:
            activity[:, band] = (
                self.rng.random(self.num_steps) < 0.75
            )

        for band in range(self.num_bands):
            if band not in high_activity_bands:
                activity[:, band] = (
                    self.rng.random(self.num_steps) < 0.15
                )

        return activity

    def _periodic_scenario(
        self,
        activity: np.ndarray,
    ) -> np.ndarray:
        """
        Selected bands exhibit periodic activity.
        """

        for band in range(self.num_bands):
            if band % 5 == 0:
                period = 10
                active_length = 4

                for time_step in range(self.num_steps):
                    activity[time_step, band] = int(
                        time_step % period < active_length
                    )
            else:
                activity[:, band] = (
                    self.rng.random(self.num_steps) < 0.12
                )

        return activity

    def _bursty_scenario(
        self,
        activity: np.ndarray,
    ) -> np.ndarray:
        """
        Activity consists mostly of short random bursts.
        """

        for band in range(self.num_bands):
            base_probability = 0.08

            activity[:, band] = (
                self.rng.random(self.num_steps)
                < base_probability
            )

            # Add occasional short bursts.
            burst_count = max(1, self.num_steps // 20)

            for _ in range(burst_count):
                start = self.rng.integers(
                    0,
                    max(1, self.num_steps - 4),
                )

                length = int(
                    self.rng.integers(2, 5)
                )

                end = min(
                    self.num_steps,
                    start + length,
                )

                activity[start:end, band] = 1

        return activity

    def _changing_scenario(
        self,
        activity: np.ndarray,
    ) -> np.ndarray:
        """
        The most useful demo scenario.

        Activity priorities change halfway through the simulation.
        """

        change_point = self.num_steps // 2

        first_priority_bands = [2, 5]
        second_priority_bands = [12, 16]

        for band in range(self.num_bands):
            if band in first_priority_bands:
                first_probability = 0.75
                second_probability = 0.10

            elif band in second_priority_bands:
                first_probability = 0.10
                second_probability = 0.75

            else:
                first_probability = 0.10
                second_probability = 0.10

            activity[:change_point, band] = (
                self.rng.random(change_point)
                < first_probability
            )

            remaining_steps = self.num_steps - change_point

            activity[change_point:, band] = (
                self.rng.random(remaining_steps)
                < second_probability
            )

        return activity

    def _mixed_scenario(
        self,
        activity: np.ndarray,
    ) -> np.ndarray:
        """
        Combination of several simple behaviours.
        Useful as a general demo environment.
        """

        for band in range(self.num_bands):
            mode = band % 4

            if mode == 0:
                # Persistent-ish
                probability = 0.65

                activity[:, band] = (
                    self.rng.random(self.num_steps)
                    < probability
                )

            elif mode == 1:
                # Periodic
                period = 12
                active_length = 4

                for time_step in range(self.num_steps):
                    activity[time_step, band] = int(
                        time_step % period < active_length
                    )

            elif mode == 2:
                # Bursty
                activity[:, band] = (
                    self.rng.random(self.num_steps)
                    < 0.12
                )

                for _ in range(4):
                    start = self.rng.integers(
                        0,
                        max(1, self.num_steps - 5),
                    )

                    activity[
                        start:min(start + 3, self.num_steps),
                        band,
                    ] = 1

            else:
                # Intermittent
                probability = 0.30

                activity[:, band] = (
                    self.rng.random(self.num_steps)
                    < probability
                )

        return activity

    def get_truth(
        self,
        time_step: int,
        band: int,
    ) -> int:
        """
        Return hidden ground truth for evaluation/debugging only.

        The scheduler should NOT use this method.
        """

        if not 0 <= time_step < self.num_steps:
            raise IndexError("time_step out of range")

        if not 0 <= band < self.num_bands:
            raise IndexError("band out of range")

        return int(self.activity[time_step, band])