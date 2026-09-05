from evaluation.benchmark import run_benchmark


def main() -> None:
    results = run_benchmark(
        scenario_name="changing",
        num_bands=20,
        num_steps=100,
        seed=42,
    )

    print("========================================")
    print("        SIH26055 SCHEDULER BENCHMARK")
    print("========================================")

    for name, result in results.items():
        basic = result["basic"]
        events = result["events"]

        print(f"\n{name}")
        print("-" * 45)

        print(f"Total scans:          {basic.total_scans}")
        print(f"True detections:     {basic.true_detections}")
        print(f"Missed detections:   {basic.missed_detections}")
        print(f"False alarms:        {basic.false_alarms}")
        print(
            f"Detection probability: "
            f"{basic.detection_probability:.2%}"
        )
        print(
            f"False alarm probability: "
            f"{basic.false_alarm_probability:.2%}"
        )
        print(
            f"Unique bands scanned: "
            f"{basic.unique_bands_scanned}"
        )
        print(f"Coverage:             {basic.coverage:.2%}")
        print(
            f"Average reward:       "
            f"{basic.average_reward:.3f}"
        )

        print("\nEvent-level evaluation:")
        print(
            f"Total events:         "
            f"{events.total_events}"
        )
        print(
            f"Intercepted events:   "
            f"{events.intercepted_events}"
        )
        print(
            f"Missed events:        "
            f"{events.missed_events}"
        )
        print(
            f"Interception ratio:   "
            f"{events.interception_ratio:.2%}"
        )
        print(
            f"Average intercept:    "
            f"{events.average_intercept_delay:.2f} steps"
        )
        print(
            f"Maximum intercept:    "
            f"{events.max_intercept_delay} steps"
        )


if __name__ == "__main__":
    main()