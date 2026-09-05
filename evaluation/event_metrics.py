from __future__ import annotations

from dataclasses import dataclass

from simulator.environment import SyntheticRFEnvironment
from simulator.scan import ScanRecord


@dataclass
class EventEvaluation:
    total_events: int
    intercepted_events: int
    missed_events: int
    interception_ratio: float
    average_intercept_delay: float
    max_intercept_delay: int


def find_activity_events(
    environment: SyntheticRFEnvironment,
) -> list[tuple[int, int]]:
    """
    Identify the start of each contiguous activity period.

    Returns:
        List of (start_time, band) tuples.
    """

    events: list[tuple[int, int]] = []

    for band in range(environment.num_bands):
        previous_state = 0

        for time_step in range(environment.num_steps):
            current_state = environment.get_truth(
                time_step,
                band,
            )

            # 0 -> 1 transition = beginning of an activity event.
            if current_state == 1 and previous_state == 0:
                events.append((time_step, band))

            previous_state = current_state

    return events


def evaluate_interception(
    environment: SyntheticRFEnvironment,
    history: list[ScanRecord],
) -> EventEvaluation:
    """
    Evaluate whether activity events were actually detected.

    An event is considered intercepted when:
    - the scheduler scans the event's band,
    - the scan occurs after the event starts,
    - the event is still active,
    - and the simulated receiver reports detected=True.

    Intercept delay is measured from event start to the first
    successful detection.
    """

    events = find_activity_events(environment)

    intercepted = 0
    delays: list[int] = []

    for event_start, band in events:
        detection_time = None

        for record in history:
            if record.band != band:
                continue

            if record.time_step < event_start:
                continue

            # The event must still be active at scan time.
            truth = environment.get_truth(
                record.time_step,
                band,
            )

            if truth != 1:
                continue

            # IMPORTANT:
            # The receiver must actually detect the activity.
            if not record.detected:
                continue

            detection_time = record.time_step
            break

        if detection_time is not None:
            intercepted += 1
            delays.append(detection_time - event_start)

    total_events = len(events)
    missed_events = total_events - intercepted

    if total_events == 0:
        interception_ratio = 0.0
    else:
        interception_ratio = intercepted / total_events

    if delays:
        average_delay = sum(delays) / len(delays)
        max_delay = max(delays)
    else:
        average_delay = 0.0
        max_delay = 0

    return EventEvaluation(
        total_events=total_events,
        intercepted_events=intercepted,
        missed_events=missed_events,
        interception_ratio=interception_ratio,
        average_intercept_delay=average_delay,
        max_intercept_delay=max_delay,
    )
