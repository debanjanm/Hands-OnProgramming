"""Cleaning: turn raw dirty tables into trustworthy ones."""
import pandas as pd

MAX_QUANTITY = 50  # anything above this (or below 1) is treated as a data-entry outlier


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate customer_ids, parse signup_date (bad -> NaT), missing country -> "Unknown".

    Return a new frame with a fresh 0..n-1 index; do not modify the input.
    """
    # TODO (milestone 2): drop_duplicates, pd.to_datetime(..., format="%Y-%m-%d", errors="coerce")
    raise NotImplementedError


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate product_ids, missing category -> "Uncategorized". Fresh index."""
    # TODO (milestone 2)
    raise NotImplementedError


def clean_orders(orders: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """Return only usable, completed orders.

    Steps: drop duplicate order_ids; parse order_date and drop rows where it is bad;
    fill a missing unit_price from `products`; drop rows with missing quantity or a quantity
    outside 1..MAX_QUANTITY; keep status == "completed". Quantity becomes int. Fresh index.
    """
    # TODO (milestone 2)
    raise NotImplementedError
