"""Validation: check the cleaned tables and report problems as readable strings."""
import pandas as pd

REQUIRED = {
    "orders": ["order_id", "customer_id", "product_id", "order_date", "quantity", "unit_price"],
    "customers": ["customer_id", "signup_date", "country"],
    "products": ["product_id", "category", "price"],
}

NULLABLE = {"signup_date"}  # a bad signup date is allowed to stay NaT; nothing here depends on it


def validate(orders: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame) -> list[str]:
    """Return a list of problems (empty list = all good)."""
    problems = []
    tables = {"orders": orders, "customers": customers, "products": products}
    for name, cols in REQUIRED.items():
        missing = [c for c in cols if c not in tables[name].columns]
        if missing:
            problems.append(f"{name}: missing columns {missing}")
    if problems:
        return problems  # can't check further without the columns

    for name, cols in REQUIRED.items():
        cols = [c for c in cols if c not in NULLABLE]
        nulls = tables[name][cols].isna().sum()
        for col, n in nulls[nulls > 0].items():
            problems.append(f"{name}.{col}: {n} missing values")
    if orders["order_id"].duplicated().any():
        problems.append("orders: duplicate order_id")
    if (orders["quantity"] <= 0).any():
        problems.append("orders: quantity must be positive")
    if (orders["unit_price"] < 0).any():
        problems.append("orders: negative unit_price")
    for col, other in [("customer_id", customers), ("product_id", products)]:
        orphans = ~orders[col].isin(other[col])
        if orphans.any():
            problems.append(f"orders: {int(orphans.sum())} rows with unknown {col}")
    return problems


def assert_valid(orders: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame) -> None:
    """Raise ValueError listing every problem, or return None."""
    problems = validate(orders, customers, products)
    if problems:
        raise ValueError("; ".join(problems))
