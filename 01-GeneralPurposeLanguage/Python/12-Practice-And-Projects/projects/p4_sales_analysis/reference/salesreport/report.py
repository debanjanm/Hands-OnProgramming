"""Markdown report writer and the one-call pipeline."""
from pathlib import Path

import pandas as pd

from . import charts, clean, features, kpis, validate
from .generate import make_dataset


def to_markdown_table(df: pd.DataFrame) -> str:
    """Render a DataFrame as a GitHub-style markdown table (no index, no extra dependency)."""
    head = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "| " + " | ".join("---" for _ in df.columns) + " |"
    rows = ["| " + " | ".join(str(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join([head, sep, *rows])


def build_report(df: pd.DataFrame, chart_files: list[Path] | None = None) -> str:
    """Return the report text: title, headline numbers, KPI tables, then chart images (if given)."""
    lines = [
        "# Sales report", "",
        f"- Orders: {df['order_id'].nunique()}",
        f"- Customers: {df['customer_id'].nunique()}",
        f"- Total revenue: {df['revenue'].sum():.2f}",
        f"- Average order value: {kpis.average_order_value(df):.2f}", "",
        "## Revenue by month", "", to_markdown_table(kpis.revenue_by_month(df)), "",
        "## Revenue by category", "", to_markdown_table(kpis.revenue_by_category(df)), "",
        "## Top customers", "", to_markdown_table(kpis.top_customers(df)), "",
    ]
    if chart_files:
        lines += ["## Charts", ""] + [f"![{Path(p).stem}]({Path(p).name})" for p in chart_files] + [""]
    return "\n".join(lines)


def write_report(df: pd.DataFrame, out_dir, chart_files: list[Path] | None = None) -> Path:
    """Write out_dir/report.md and return its path."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "report.md"
    path.write_text(build_report(df, chart_files), encoding="utf-8")
    return path


def run_pipeline(out_dir, seed: int = 42) -> dict:
    """generate -> clean -> validate -> features -> charts -> report. Returns paths and the features table."""
    raw = make_dataset(seed)
    customers = clean.clean_customers(raw["customers"])
    products = clean.clean_products(raw["products"])
    orders = clean.clean_orders(raw["orders"], products)
    validate.assert_valid(orders, customers, products)
    df = features.add_features(orders, customers, products)
    chart_files = charts.make_all(df, out_dir)
    return {"report": write_report(df, out_dir, chart_files), "charts": chart_files, "features": df}
