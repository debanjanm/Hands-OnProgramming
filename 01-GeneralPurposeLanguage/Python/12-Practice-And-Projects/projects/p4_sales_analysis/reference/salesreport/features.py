"""Feature engineering: one wide table, one row per order."""
import pandas as pd


def add_features(orders: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """Join orders with customer country and product category, then add:

    revenue          quantity * unit_price
    order_month      "YYYY-MM" string
    first_month      each customer's first order_month ("cohort")
    cohort_index     whole months between first_month and order_month (0 for the first month)
    """
    df = orders.merge(customers[["customer_id", "country"]], on="customer_id", how="left")
    df = df.merge(products[["product_id", "category"]], on="product_id", how="left")
    df["revenue"] = df["quantity"] * df["unit_price"]
    df["order_month"] = df["order_date"].dt.strftime("%Y-%m")
    df["first_month"] = df.groupby("customer_id")["order_month"].transform("min")
    months = df["order_date"].dt.year * 12 + df["order_date"].dt.month
    first = pd.to_datetime(df["first_month"] + "-01")
    df["cohort_index"] = months - (first.dt.year * 12 + first.dt.month)
    return df
