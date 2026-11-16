"""Cleaning: turn raw dirty tables into trustworthy ones."""
import pandas as pd

MAX_QUANTITY = 50  # anything above this (or below 1) is treated as a data-entry outlier


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate customer_ids, parse signup_date (bad -> NaT), missing country -> "Unknown"."""
    out = df.drop_duplicates("customer_id").copy()
    out["signup_date"] = pd.to_datetime(out["signup_date"], format="%Y-%m-%d", errors="coerce")
    out["country"] = out["country"].astype("object").where(out["country"].notna(), "Unknown")
    return out.reset_index(drop=True)


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate product_ids, missing category -> "Uncategorized"."""
    out = df.drop_duplicates("product_id").copy()
    out["category"] = out["category"].astype("object").where(out["category"].notna(), "Uncategorized")
    return out.reset_index(drop=True)


def clean_orders(orders: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """Return only usable, completed orders.

    Steps: drop duplicate order_ids; parse order_date and drop rows where it is bad;
    fill a missing unit_price from `products`; drop rows with missing quantity or a quantity
    outside 1..MAX_QUANTITY; keep status == "completed". Quantity becomes int.
    """
    out = orders.drop_duplicates("order_id").copy()
    out["order_date"] = pd.to_datetime(out["order_date"], format="%Y-%m-%d", errors="coerce")
    out = out.dropna(subset=["order_date", "quantity"])
    list_price = out["product_id"].map(products.drop_duplicates("product_id").set_index("product_id")["price"])
    out["unit_price"] = out["unit_price"].where(out["unit_price"].notna(), list_price)
    out = out.dropna(subset=["unit_price"])
    out = out[out["quantity"].between(1, MAX_QUANTITY) & (out["status"] == "completed")].copy()
    out["quantity"] = out["quantity"].astype(int)
    return out.reset_index(drop=True)
