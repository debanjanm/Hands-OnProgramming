"""Synthetic, seeded sales data with deliberate dirt."""
import numpy as np
import pandas as pd

CATEGORIES = ["Books", "Games", "Garden", "Kitchen"]
COUNTRIES = ["UK", "US", "DE", "IN"]
STATUSES = ["completed", "cancelled"]


def make_dataset(seed: int = 42, n_customers: int = 120, n_orders: int = 800) -> dict[str, pd.DataFrame]:
    """Return {"customers", "products", "orders"} as DataFrames of raw (dirty) data.

    Same seed -> identical output (use np.random.default_rng(seed)). Dates are YYYY-MM-DD strings,
    except the bad ones.
    Columns:
      customers: customer_id, name, signup_date, country
      products:  product_id, name, category, price          (12 products)
      orders:    order_id, customer_id, product_id, order_date, quantity, unit_price, status
    Dirt to add on purpose:
      customers: duplicate rows, missing country, unparseable signup_date (e.g. "yesterday")
      products:  one duplicate row, one missing category
      orders:    duplicate rows, missing quantity, missing unit_price, bad order_date
                 ("31/02/2023", "not a date"), outlier quantity (500), some "cancelled" orders
    """
    # TODO (milestone 1)
    raise NotImplementedError
