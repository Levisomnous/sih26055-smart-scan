from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from .environment import SyntheticRFEnvironment


def plot_environment(
    environment: SyntheticRFEnvironment,
    output_path: str = "data/rf_environment.png",
) -> None:
    """
    Generate and save a heatmap showing the simulated
    ground-truth activity across frequency bands and time.
    """

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(12, 7))

    plt.imshow(
        environment.activity.T,
        aspect="auto",
        interpolation="nearest",
    )

    plt.xlabel("Time Step")
    plt.ylabel("Frequency Band")
    plt.title("Synthetic RF Environment — Ground Truth")

    plt.colorbar(
        label="Activity (0 = inactive, 1 = active)"
    )

    plt.yticks(
        range(environment.num_bands),
        [f"B{i + 1}" for i in range(environment.num_bands)],
    )

    plt.tight_layout()

    # Save instead of attempting to open a GUI window.
    plt.savefig(output_file, dpi=150, bbox_inches="tight")

    plt.close()

    print(f"Heatmap saved to: {output_file}")