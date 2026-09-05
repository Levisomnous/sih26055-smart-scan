from simulator.environment import (
    ScenarioConfig,
    SyntheticRFEnvironment,
)

from dashboard.demo_runner import DemoRunner


def main() -> None:

    config = ScenarioConfig(
        name="changing",
        num_bands=20,
        num_steps=10,
        seed=42,
    )

    environment = SyntheticRFEnvironment(config)

    runner = DemoRunner(
        environment=environment,
        seed=42,
    )

    print("=== LIVE DEMO TEST ===")

    for _ in range(10):

        state = runner.step()

        result = (
            "DETECTED"
            if state.detected
            else "NOT DETECTED"
        )

        print(
            f"Time {state.time_step:02d} | "
            f"Band B{state.selected_band + 1:02d} | "
            f"{result} | "
            f"Reward {state.reward:.1f}"
        )

    print("\nCurrent band scores:")

    scores = runner.get_scores()

    for band, score in enumerate(scores):
        print(
            f"B{band + 1:02d}: "
            f"{score:.2f}"
        )


if __name__ == "__main__":
    main()