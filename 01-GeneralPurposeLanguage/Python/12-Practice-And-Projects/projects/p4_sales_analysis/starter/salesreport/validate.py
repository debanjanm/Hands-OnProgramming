"""Validation: check the cleaned tables and report problems as readable strings."""
import pandas as pd

REQUIRED = {
    "orders": ["order_id", "customer_id", "product_id", "order_date", "quantity", "unit_price"],
    "customers": ["customer_id", "signup_date", "country"],
    "products": ["product_id", "category", "price"],
}
NULLABLE = {"signup_date"}  # a bad signup date is allowed to stay NaT


def validate(orders: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame) -> list[str]:
    """Return a list of problems (empty list = all good).

    Messages the tests look for:
      "<table>: missing columns ['a', 'b']"   (stop checking after this)
      "<table>.<col>: <n> missing values"     (skip NULLABLE columns)
      "orders: duplicate order_id"
      "orders: quantity must be positive"
      "orders: negative unit_price"
      "orders: <n> rows with unknown customer_id"  (same for product_id)
    """
    # TODO (milestone 3)
    raise NotImplementedError


def assert_valid(orders: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame) -> None:
    """Raise ValueError("; ".join(problems)) if validate() finds anything."""
    # TODO (milestone 3)
    raise NotImplementedError
