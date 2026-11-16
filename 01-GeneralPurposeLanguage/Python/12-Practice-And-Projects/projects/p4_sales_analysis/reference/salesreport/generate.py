"""Synthetic, seeded sales data with deliberate dirt."""
import numpy as np
import pandas as pd

CATEGORIES = ["Books", "Games", "Garden", "Kitchen"]
COUNTRIES = ["UK", "US", "DE", "IN"]
STATUSES = ["completed", "cancelled"]


def make_dataset(seed: int = 42, n_customers: int = 120, n_orders: int = 800) -> dict[str, pd.DataFrame]:
    """Return {"customers", "products", "orders"} as DataFrames of raw (dirty) data.

    Same seed -> identical output. Dates are strings in YYYY-MM-DD form, except the bad ones.
    Dirt added on purpose:
      customers: duplicate rows, missing country, unparseable signup_date
      products:  one duplicate row, one missing category
      orders:    duplicate rows, missing quantity, missing unit_price, bad order_date,
                 outlier quantity (500), some cancelled orders
    """
    rng = np.random.default_rng(seed)

    products = pd.DataFrame({
        "product_id": np.arange(1, 13),
        "name": [f"Product {i}" for i in range(1, 13)],
        "category": [CATEGORIES[i % 4] for i in range(12)],
        "price": np.round(rng.uniform(5, 80, 12), 2),
    })

    signup = pd.Timestamp("2023-01-01") + pd.to_timedelta(rng.integers(0, 180, n_customers), unit="D")
    customers = pd.DataFrame({
        "customer_id": np.arange(1, n_customers + 1),
        "name": [f"Customer {i}" for i in range(1, n_customers + 1)],
        "signup_date": signup.strftime("%Y-%m-%d"),
        "country": rng.choice(COUNTRIES, n_customers),
    })

    cust = rng.integers(1, n_customers + 1, n_orders)
    offset = rng.integers(0, 300, n_orders)
    dates = customers["signup_date"].pipe(pd.to_datetime).to_numpy()[cust - 1] + offset.astype("timedelta64[D]")
    dates = pd.DatetimeIndex(pd.Series(dates).clip(upper=pd.Timestamp("2023-12-31")))
    pid = rng.integers(1, 13, n_orders)
    orders = pd.DataFrame({
        "order_id": np.arange(1000, 1000 + n_orders),
        "customer_id": cust,
        "product_id": pid,
        "order_date": dates.strftime("%Y-%m-%d"),
        "quantity": rng.integers(1, 6, n_orders).astype(float),
        "unit_price": products["price"].to_numpy()[pid - 1],
        "status": rng.choice(STATUSES, n_orders, p=[0.92, 0.08]),
    })

    # ---- dirt (positions drawn from the same rng, so it is reproducible)
    def pick(n, k):
        return rng.choice(n, size=k, replace=False)

    orders.loc[pick(n_orders, n_orders // 30), "order_date"] = "31/02/2023"
    orders.loc[pick(n_orders, n_orders // 50), "order_date"] = "not a date"
    orders.loc[pick(n_orders, n_orders // 40), "quantity"] = np.nan
    orders.loc[pick(n_orders, n_orders // 30), "unit_price"] = np.nan
    orders.loc[pick(n_orders, n_orders // 80), "quantity"] = 500.0
    orders = pd.concat([orders, orders.iloc[pick(n_orders, n_orders // 30)]], ignore_index=True)

    customers.loc[pick(n_customers, 5), "country"] = None
    customers.loc[pick(n_customers, 3), "signup_date"] = "yesterday"
    customers = pd.concat([customers, customers.iloc[pick(n_customers, 4)]], ignore_index=True)

    products.loc[3, "category"] = None
    products = pd.concat([products, products.iloc[[0]]], ignore_index=True)

    return {"customers": customers, "products": products, "orders": orders}
