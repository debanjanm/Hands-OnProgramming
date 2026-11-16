"""Charts saved as PNG files. Uses the non-interactive Agg backend."""
import os

os.environ.setdefault("MPLBACKEND", "Agg")  # must happen before importing matplotlib

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from pathlib import Path  # noqa: E402


def plot_revenue_by_month(monthly: pd.DataFrame, out_dir) -> Path:
    """Line chart from revenue_by_month() saved as out_dir/revenue_by_month.png; return the path.

    Create out_dir if needed (Path.mkdir(parents=True, exist_ok=True)) and plt.close(fig) afterwards.
    """
    # TODO (milestone 7)
    raise NotImplementedError


def plot_revenue_by_category(cats: pd.DataFrame, out_dir) -> Path:
    """Bar chart from revenue_by_category() saved as out_dir/revenue_by_category.png."""
    # TODO (milestone 7)
    raise NotImplementedError


def plot_cohort_heatmap(retention: pd.DataFrame, out_dir) -> Path:
    """Heatmap (ax.imshow, values 0..1) from cohort_retention() saved as out_dir/cohort_retention.png."""
    # TODO (milestone 7)
    raise NotImplementedError


def make_all(df: pd.DataFrame, out_dir) -> list[Path]:
    """Build the three KPI tables from `df` (the features table) and save all three charts.

    Return the paths in this order: month, category, cohort.
    """
    # TODO (milestone 7)
    raise NotImplementedError
