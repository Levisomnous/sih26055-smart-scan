from __future__ import annotations

from dataclasses import dataclass

from simulator.scan import ScanRecord


@dataclass
class EvaluationResult:
    total_scans: int

    true_detections: int
    missed_detections: int
    false_alarms: int
    correct_negatives: int

    detection_probability: float
    false_alarm_probability: float

    unique_bands_scanned: int
    coverage: float
    average_reward: float


def calculate_metrics(
    history: list[ScanRecord],
    num_bands: int,
) -> EvaluationResult:

    if num_bands <= 0:
        raise ValueError(
            "num_bands must be greater than 0"
        )

    total_scans = len(history)

    if total_scans == 0:
        return EvaluationResult(
            total_scans=0,
            true_detections=0,
            missed_detections=0,
            false_alarms=0,
            correct_negatives=0,
            detection_probability=0.0,
            false_alarm_probability=0.0,
            unique_bands_scanned=0,
            coverage=0.0,
            average_reward=0.0,
        )

    true_detections = sum(
        record.truth_active and record.detected
        for record in history
    )

    missed_detections = sum(
        record.truth_active and not record.detected
        for record in history
    )

    false_alarms = sum(
        not record.truth_active and record.detected
        for record in history
    )

    correct_negatives = sum(
        not record.truth_active and not record.detected
        for record in history
    )

    actual_active_scans = (
        true_detections + missed_detections
    )

    actual_inactive_scans = (
        false_alarms + correct_negatives
    )

    if actual_active_scans > 0:
        detection_probability = (
            true_detections / actual_active_scans
        )
    else:
        detection_probability = 0.0

    if actual_inactive_scans > 0:
        false_alarm_probability = (
            false_alarms / actual_inactive_scans
        )
    else:
        false_alarm_probability = 0.0

    unique_bands = {
        record.band
        for record in history
    }

    unique_bands_scanned = len(unique_bands)

    coverage = unique_bands_scanned / num_bands

    # Simple reward:
    # true detection = +1
    # false alarm = -1
    # miss/correct negative = 0
    total_reward = (
        true_detections
        - false_alarms
    )

    average_reward = total_reward / total_scans

    return EvaluationResult(
        total_scans=total_scans,
        true_detections=true_detections,
        missed_detections=missed_detections,
        false_alarms=false_alarms,
        correct_negatives=correct_negatives,
        detection_probability=detection_probability,
        false_alarm_probability=false_alarm_probability,
        unique_bands_scanned=unique_bands_scanned,
        coverage=coverage,
        average_reward=average_reward,
    )