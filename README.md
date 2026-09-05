# SIH26055 — Smart Scan Strategy for Electronic Warfare

A safe, academic simulation prototype for intelligent scan scheduling in a synthetic RF environment.

This project evaluates whether an adaptive scheduler can use previous scan observations to decide which simulated frequency band should be scanned next.

> **Safety scope:** This project is a synthetic simulation only. It does not perform real RF interception, electronic attack, jamming, hostile-emitter exploitation, or operational military targeting.

## 1. Problem

Electronic-spectrum scanning can be inefficient when a receiver repeatedly checks channels without considering previous observations.

This prototype models scan scheduling as a sequential decision problem:

1. A synthetic environment generates activity across simulated frequency bands.
2. A simulated receiver observes the selected band.
3. The receiver returns a detection or non-detection observation.
4. The scheduler updates its internal state.
5. The scheduler selects the next band.
6. Performance is evaluated using detection, false-alarm, coverage, reward, and event-interception metrics.

The objective is to demonstrate adaptive decision-making in a controlled synthetic environment.

## 2. Implemented System

The current prototype contains:

- Synthetic RF environment
- Configurable activity scenarios
- Simulated receiver
- Sequential baseline scheduler
- Random baseline scheduler
- Simple Adaptive scheduler
- Smart Adaptive scheduler
- Scan history
- Event-level evaluation
- Reproducible benchmark runner
- Multi-seed evaluation
- Streamlit dashboard
- Automated pytest tests

No real SDR hardware or live RF input is required.

## 3. Architecture

```text
Synthetic RF Environment
          |
          v
   Simulated Receiver
          |
          v
      Observation
          |
          v
       Scheduler
          |
          v
    Select Next Band
          |
          v
      Scan History
          |
          v
      Evaluation


simulator/
    environment.py
    receiver.py
    scan.py
    visualization.py

scheduler/
    base.py
    sequential.py
    random_scheduler.py
    adaptive.py
    smart_adaptive.py

evaluation/
    metrics.py
    event_metrics.py
    runner.py
    benchmark.py
    multiseed.py

dashboard/
    app.py
    demo_runner.py

tests/
    test_demo_runner.py
    test_evaluation.py
