"""Markdown report writer and the one-call pipeline."""
from pathlib import Path

import pandas as pd

from . import charts, clean, features, kpis, validate  # noqa: F401
from .generate import make_dataset  # noqa: F401


def to_markdown_table(df: pd.DataFrame) -> str:
    """Render a DataFrame as a markdown table, no index:

        | a | b |
        | --- | --- |
        | 1 | x |
    """
    # TODO (milestone 8): df.itertuples(index=False)
    raise NotImplementedError


def build_report(df: pd.DataFrame, chart_files: list[Path] | None = None) -> str:
    """Return the report text. Must contain, in order:

    "# Sales report", bullets "- Orders: N", "- Customers: N", "- Total revenue: 0.00",
    "- Average order value: 0.00", then sections "## Revenue by month", "## Revenue by category",
    "## Top customers" each followed by a table, and - only if chart_files is given -
    "## Charts" with lines like "![revenue_by_month](revenue_by_month.png)" (file stem and file name).
    """
    # TODO (milestone 8)
    raise NotImplementedError


def write_report(df: pd.DataFrame, out_dir, chart_files: list[Path] | None = None) -> Path:
    """Write out_dir/report.md (create the folder if needed) and return its path."""
    # TODO (milestone 8)
    raise NotImplementedError


def run_pipeline(out_dir, seed: int = 42) -> dict:
    """generate -> clean -> validate -> features -> charts -> report.

    Return {"report": Path, "charts": list[Path], "features": DataFrame}.
    """
    # TODO (milestone 9)
    raise NotImplementedError
