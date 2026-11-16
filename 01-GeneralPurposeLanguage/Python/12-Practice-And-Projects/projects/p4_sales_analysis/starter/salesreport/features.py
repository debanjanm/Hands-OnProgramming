"""Feature engineering: one wide table, one row per order."""
import pandas as pd


def add_features(orders: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """Join orders with customer country and product category, then add:

    revenue          quantity * unit_price
    order_month      "YYYY-MM" string
    first_month      each customer's first order_month ("cohort")
    cohort_index     whole months between first_month and order_month (0 for the first month)

    Do not modify the inputs.
    """
    # TODO (milestone 4): merge x2, groupby(...).transform("min"), year*12+month arithmetic
    raise NotImplementedError
