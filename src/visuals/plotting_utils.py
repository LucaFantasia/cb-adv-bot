from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def finalise_plot(fig: Figure, save: bool, show: bool, path: Path | None = None) -> None:
    """
    Handles save/show logic for all plot types to ensure consistency across visuals.

    Args:
        fig: Matplotlib figure object
        save: Whether to save the plot to disk
        show: Whether to show the plot on screen
        filename: Optional path for saving the figure
    """
    if save and path:
        fig.savefig(path)
    if not show:
        plt.close(fig)
