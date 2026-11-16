"""ex11_pandas - pandas practice: selection, cleaning, groupby, merge, reshape, time, strings.

Avoid Python loops over rows. Never change the DataFrame you are given; return a new one.
"""
import pandas as pd


def adult_contacts(df):
    """Return rows where age >= 18, keeping only the columns 'name' and 'city'
    (in that order) and the original index.

    Example: people aged 12 and 30 -> only the 30 year old row remains.
    Level: easy
    Hint: df.loc[mask, ["name", "city"]]
    """
    raise NotImplementedError


def fill_missing(df):
    """Fill missing 'price' with the median price and missing 'category' with "unknown".
    Return a new DataFrame; other columns stay as they are.

    Example: price [1, NaN, 3] -> [1, 2, 3]; category [NaN] -> ["unknown"]
    Level: easy
    Hint: df.fillna({...}) accepts a dict of column -> value.
    """
    raise NotImplementedError


def clean_names(s):
    """Clean a Series of names: strip the ends, squeeze repeated inner spaces into one,
    and use Title Case. Missing values stay missing.

    Example: "  aNNa   maria " -> "Anna Maria"
    Level: easy
    Hint: the .str accessor; str.replace with regex=True and r"\\s+".
    """
    raise NotImplementedError


def add_store_share(df):
    """Add a column 'share' = amount / total amount of that row's 'store'.
    Return a new DataFrame with all original columns plus 'share'.

    Example: store X amounts 1 and 3 -> share 0.25 and 0.75
    Level: medium
    Hint: groupby("store")["amount"].transform("sum") keeps the original row shape.
    """
    raise NotImplementedError


def team_summary(df):
    """Per 'team' return a DataFrame indexed by team with columns
    n (row count), avg (mean score) and best (max score).

    Example: team A scores 10, 20 -> n=2, avg=15.0, best=20
    Level: medium
    Hint: named aggregation: .agg(n=("score", "size"), ...)
    """
    raise NotImplementedError


def orders_with_names(orders, customers):
    """Attach the customer's 'name' to every order (orders: order_id, customer_id, amount;
    customers: customer_id, name). Keep all orders; unknown customers get name "Unknown".
    Keep the order of orders and return columns order_id, customer_id, amount, name.

    Example: order for customer 99 who is not in customers -> name "Unknown"
    Level: medium
    Hint: how="left" merge, then fillna on the new column.
    """
    raise NotImplementedError


def sales_table(df):
    """Make a table with one row per 'region' and one column per 'month', containing the
    sum of 'sales'. Missing combinations are 0.

    Example: (N, Jan, 5), (N, Jan, 2), (S, Feb, 4) -> N/Jan 7, N/Feb 0, S/Jan 0, S/Feb 4
    Level: medium
    Hint: pivot_table(index=..., columns=..., values=..., aggfunc="sum", fill_value=0)
    """
    raise NotImplementedError


def scores_long(df):
    """Turn a wide table (columns: student, math, art) into a long one with columns
    student, subject, score; sorted by student then subject, with a fresh index.

    Example: (ann, math=90, art=80) -> (ann, art, 80), (ann, math, 90)
    Level: medium
    Hint: melt(id_vars=..., var_name=..., value_name=...) then sort_values.
    """
    raise NotImplementedError


def monthly_totals(df):
    """df has a datetime column 'date' and a number column 'amount'. Return a Series of
    total amount per calendar month, indexed by the first day of the month.
    Months with no rows appear with 0.

    Example: Jan 5 + Jan 5, Mar 1 -> Jan 10, Feb 0, Mar 1
    Level: medium
    Hint: set_index("date")["amount"].resample("MS").sum()
    """
    raise NotImplementedError


def top_n_per_group(df, n):
    """For each 'group' keep the n rows with the highest 'score' (highest first inside the
    group). Return rows ordered by group, then score descending, with a fresh index.
    Ties are kept in original row order.

    Example: n=1 -> the best row of every group
    Level: hard
    Hint: sort_values by score descending (stable), then groupby("group").head(n), then sort by group.
    """
    raise NotImplementedError


def add_rank_in_group(df):
    """Add an int column 'rank' = position of the row's 'score' inside its 'group'
    (1 = highest). Equal scores share the same, lowest rank (1, 1, 3 ...).

    Example: scores 90, 90, 70 in one group -> ranks 1, 1, 3
    Level: hard
    Hint: groupby("group")["score"].rank(method="min", ascending=False).astype(int)
    """
    raise NotImplementedError


def clean_sales(raw):
    """Clean a messy sales table in ONE method chain. Input columns (any spelling of case
    and spaces around the names): ' Date', 'Region ', 'AMOUNT'. Steps:
      1. column names -> stripped lower case
      2. drop exact duplicate rows
      3. 'date' -> datetime (bad values become NaT), drop rows with missing date or amount
      4. 'region' -> stripped Title Case
      5. add 'month' = month number (int)
      6. sort by date, fresh index
    Return columns date, region, amount, month.

    Example: ("2024-01-05", " north ", 10) -> (Timestamp 2024-01-05, "North", 10, 1)
    Level: hard
    Hint: use .rename, .drop_duplicates, .assign (with lambdas), .dropna, .sort_values, .reset_index.
    """
    raise NotImplementedError
