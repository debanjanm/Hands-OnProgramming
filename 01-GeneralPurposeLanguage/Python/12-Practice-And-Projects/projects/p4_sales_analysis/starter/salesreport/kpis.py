"""KPIs computed from the feature table."""
import pandas as pd


def revenue_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Columns [order_month, revenue], sorted by month, revenue rounded to 2 dp, fresh index."""
    # TODO (milestone 5)
    raise NotImplementedError


def revenue_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Columns [category, revenue], biggest first (ties by category name), fresh index."""
    # TODO (milestone 5)
    raise NotImplementedError


def top_customers(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Columns [customer_id, orders, revenue] for the n biggest spenders (ties by customer_id).

    `orders` = number of distinct order_ids. Revenue rounded to 2 dp.
    """
    # TODO (milestone 5): groupby + agg with named aggregation
    raise NotImplementedError


def average_order_value(df: pd.DataFrame) -> float:
    """Total revenue / number of distinct orders, rounded to 2 dp. 0.0 for an empty table."""
    # TODO (milestone 5)
    raise NotImplementedError


def cohort_retention(df: pd.DataFrame) -> pd.DataFrame:
    """Share of each cohort's customers that ordered k months after their first order.

    Rows = first_month (index name "first_month"), columns = cohort_index 0..max (no gaps),
    values 0..1 rounded to 4 dp. Column 0 is always 1.0. Months with nobody active show 0.0.
    Hint: groupby([first_month, cohort_index])["customer_id"].nunique().unstack(fill_value=0),
    then divide every row by its column-0 value.
    """
    # TODO (milestone 6)
    raise NotImplementedError
