"""KPIs computed from the feature table."""
import pandas as pd


def revenue_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Columns [order_month, revenue], sorted by month, revenue rounded to 2 dp."""
    out = df.groupby("order_month", as_index=False)["revenue"].sum().sort_values("order_month")
    out["revenue"] = out["revenue"].round(2)
    return out.reset_index(drop=True)


def revenue_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Columns [category, revenue], biggest first (ties by category name)."""
    out = df.groupby("category", as_index=False)["revenue"].sum()
    out["revenue"] = out["revenue"].round(2)
    return out.sort_values(["revenue", "category"], ascending=[False, True]).reset_index(drop=True)


def top_customers(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Columns [customer_id, orders, revenue] for the n biggest spenders (ties by customer_id)."""
    out = df.groupby("customer_id").agg(orders=("order_id", "nunique"), revenue=("revenue", "sum")).reset_index()
    out["revenue"] = out["revenue"].round(2)
    return out.sort_values(["revenue", "customer_id"], ascending=[False, True]).head(n).reset_index(drop=True)


def average_order_value(df: pd.DataFrame) -> float:
    """Total revenue / number of distinct orders, rounded to 2 dp. 0.0 for an empty table."""
    n = df["order_id"].nunique()
    return round(float(df["revenue"].sum() / n), 2) if n else 0.0


def cohort_retention(df: pd.DataFrame) -> pd.DataFrame:
    """Share of each cohort's customers that ordered again k months after their first order.

    Rows = first_month, columns = cohort_index (0, 1, 2, ...), values in 0..1 rounded to 4 dp,
    Column 0 is always 1.0. A month with no active customers (or not reached yet) shows 0.0.
    """
    active = df.groupby(["first_month", "cohort_index"])["customer_id"].nunique().unstack(fill_value=0)
    active = active.reindex(columns=range(active.columns.max() + 1), fill_value=0)  # no gaps in 0..max
    retention = active.div(active[0], axis=0).round(4)
    retention.columns.name = None
    retention.index.name = "first_month"
    return retention
