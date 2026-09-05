from __future__ import annotations

import csv
from pathlib import Path
from statistics import mean, median, stdev

from evaluation.benchmark import run_benchmark


METRICS = [
    "detection_probability",
    "false_alarm_probability",
    "interception_ratio",
    "average_intercept_delay",
    "average_reward",
    "coverage",
]


def run_multiseed(
    scenarios: list[str],
    seeds: list[int],
    num_bands: int = 20,
    num_steps: int = 100,
) -> list[dict]:
    """
    Run the benchmark across multiple scenarios and seeds.

    Each row contains the raw result for one:
        scenario × seed × strategy
    """

    rows: list[dict] = []

    for scenario in scenarios:
        for seed in seeds:

            results = run_benchmark(
                scenario_name=scenario,
                num_bands=num_bands,
                num_steps=num_steps,
                seed=seed,
            )

            for strategy, result in results.items():
                basic = result["basic"]
                events = result["events"]

                rows.append(
                    {
                        "scenario": scenario,
                        "seed": seed,
                        "strategy": strategy,
                        "detection_probability":
                            basic.detection_probability,
                        "false_alarm_probability":
                            basic.false_alarm_probability,
                        "interception_ratio":
                            events.interception_ratio,
                        "average_intercept_delay":
                            events.average_intercept_delay,
                        "average_reward":
                            basic.average_reward,
                        "coverage":
                            basic.coverage,
                    }
                )

    return rows


def summarize_results(
    rows: list[dict],
) -> list[dict]:
    """
    Calculate mean/std/median/min/max for each
    scenario × strategy × metric.
    """

    groups: dict[tuple[str, str], list[dict]] = {}

    for row in rows:
        key = (
            row["scenario"],
            row["strategy"],
        )

        groups.setdefault(key, []).append(row)

    summaries: list[dict] = []

    for (scenario, strategy), group_rows in groups.items():

        for metric in METRICS:

            values = [
                float(row[metric])
                for row in group_rows
            ]

            summaries.append(
                {
                    "scenario": scenario,
                    "strategy": strategy,
                    "metric": metric,
                    "mean": mean(values),
                    "std": (
                        stdev(values)
                        if len(values) > 1
                        else 0.0
                    ),
                    "median": median(values),
                    "min": min(values),
                    "max": max(values),
                }
            )

    return summaries


def save_csv(
    path: str,
    rows: list[dict],
) -> None:
    """
    Save raw multi-seed results as CSV.
    """

    output = Path(path)
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not rows:
        return

    fieldnames = list(rows[0].keys())

    with output.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)


def print_summary(
    summaries: list[dict],
) -> None:
    """
    Print human-readable summary.
    """

    print("=" * 95)
    print("SIH26055 MULTI-SEED BENCHMARK")
    print("=" * 95)

    scenarios = sorted(
        {row["scenario"] for row in summaries}
    )

    for scenario in scenarios:

        print(
            f"\nSCENARIO: {scenario}"
        )
        print("-" * 95)

        for metric in METRICS:

            print(
                f"\n{metric}"
            )

            print(
                f"{'Strategy':20s} "
                f"{'Mean':>10s} "
                f"{'Std':>10s} "
                f"{'Median':>10s} "
                f"{'Min':>10s} "
                f"{'Max':>10s}"
            )

            print("-" * 75)

            metric_rows = [
                row
                for row in summaries
                if row["scenario"] == scenario
                and row["metric"] == metric
            ]

            for row in metric_rows:
                print(
                    f"{row['strategy']:20s} "
                    f"{row['mean']:10.4f} "
                    f"{row['std']:10.4f} "
                    f"{row['median']:10.4f} "
                    f"{row['min']:10.4f} "
                    f"{row['max']:10.4f}"
                )


def main() -> None:
    scenarios = [
        "periodic",
        "bursty",
        "mixed",
    ]

    seeds = list(range(1, 21))

    raw_results = run_multiseed(
        scenarios=scenarios,
        seeds=seeds,
        num_bands=20,
        num_steps=100,
    )

    summaries = summarize_results(
        raw_results
    )

    save_csv(
        "data/multiseed_raw.csv",
        raw_results,
    )

    save_csv(
        "data/multiseed_summary.csv",
        summaries,
    )

    print_summary(summaries)

    print("\nSaved:")
    print("  data/multiseed_raw.csv")
    print("  data/multiseed_summary.csv")


if __name__ == "__main__":
    main()
