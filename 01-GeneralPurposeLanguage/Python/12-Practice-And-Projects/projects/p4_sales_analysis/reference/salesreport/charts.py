"""Charts saved as PNG files. Uses the non-interactive Agg backend."""
import os

os.environ.setdefault("MPLBACKEND", "Agg")  # must happen before importing matplotlib

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from pathlib import Path  # noqa: E402


def _save(fig, out_dir, name) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / name
    fig.tight_layout()
    fig.savefig(path, dpi=80)
    plt.close(fig)
    return path


def plot_revenue_by_month(monthly: pd.DataFrame, out_dir) -> Path:
    """Line chart from revenue_by_month() -> out_dir/revenue_by_month.png"""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(monthly["order_month"], monthly["revenue"], marker="o")
    ax.set(title="Revenue by month", xlabel="Month", ylabel="Revenue")
    ax.tick_params(axis="x", rotation=45)
    return _save(fig, out_dir, "revenue_by_month.png")


def plot_revenue_by_category(cats: pd.DataFrame, out_dir) -> Path:
    """Bar chart from revenue_by_category() -> out_dir/revenue_by_category.png"""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(cats["category"], cats["revenue"])
    ax.set(title="Revenue by category", ylabel="Revenue")
    return _save(fig, out_dir, "revenue_by_category.png")


def plot_cohort_heatmap(retention: pd.DataFrame, out_dir) -> Path:
    """Heatmap from cohort_retention() -> out_dir/cohort_retention.png"""
    fig, ax = plt.subplots(figsize=(7, 4))
    im = ax.imshow(retention.to_numpy(dtype=float), vmin=0, vmax=1, cmap="Blues", aspect="auto")
    ax.set_xticks(np.arange(retention.shape[1]), labels=[str(c) for c in retention.columns])
    ax.set_yticks(np.arange(retention.shape[0]), labels=list(retention.index))
    ax.set(title="Cohort retention", xlabel="Months since first order", ylabel="Cohort")
    fig.colorbar(im, ax=ax)
    return _save(fig, out_dir, "cohort_retention.png")


def make_all(df: pd.DataFrame, out_dir) -> list[Path]:
    """Build the three KPI tables from `df` (features table) and save all charts."""
    from . import kpis
    return [
        plot_revenue_by_month(kpis.revenue_by_month(df), out_dir),
        plot_revenue_by_category(kpis.revenue_by_category(df), out_dir),
        plot_cohort_heatmap(kpis.cohort_retention(df), out_dir),
    ]
