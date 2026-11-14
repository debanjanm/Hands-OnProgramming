# 01. Column Selection: df['col'] vs df[['col1','col2']] vs df.col
# 02. .loc[] (label-based) vs .iloc[] (position-based)
# 03. .at[] / .iat[] for Fast Scalar Access
# 04. Boolean / Mask Filtering
# 05. Combining Conditions with & / | (and why 'and'/'or' fail)
# 06. The SettingWithCopyWarning Gotcha

import pandas as pd
import numpy as np

orders = pd.DataFrame({
    "order_id": [101, 102, 103, 104, 105],
    "customer": ["Alice", "Bob", "Carla", "Dev", "Eve"],
    "amount": [250.0, 80.5, 430.0, 15.75, 999.0],
    "status": ["shipped", "pending", "shipped", "cancelled", "shipped"],
}, index=["a", "b", "c", "d", "e"])  # custom labels, deliberately NOT 0..n-1

print("orders:\n", orders, sep="")

# 01. Column Selection
# ------------------------------------
# - df['col']          -> a single Series (works for any column name).
# - df[['c1', 'c2']]    -> a DataFrame subset (note the DOUBLE brackets -
#   the outer [] indexes df, the inner [] is a Python list of names).
# - df.col              -> attribute access, only works if the name is a
#   valid Python identifier, doesn't collide with a DataFrame method/attr
#   (e.g. df.count, df.shape), and is a SINGLE name - can't do df.col1,col2.
# - Bracket-with-list is the only form that is safe for MULTIPLE or
#   DYNAMIC (variable) column names - attribute access can't take a
#   variable, and single-bracket can't take more than one name at once.

print("\n# 01. Column Selection")
print("# ------------------------------------")

print("orders['customer'] (Series):\n", orders["customer"], sep="")
print("\norders[['customer', 'amount']] (DataFrame, note double brackets):\n", orders[["customer", "amount"]], sep="")
print("\norders.amount (attribute access, same Series as orders['amount']):\n", orders.amount, sep="")

dynamic_cols = ["order_id", "status"]
print("\nDynamic column list ->", dynamic_cols)
print("orders[dynamic_cols] works; orders.dynamic_cols would NOT (looks for a literal attribute named 'dynamic_cols'):")
print(orders[dynamic_cols])
print("# Gotcha: a column literally named 'count', 'shape', etc. shadows a DataFrame method via dot")
print("#   access and can silently break code that expects the method - another reason to prefer df['col'].")

# 02. .loc[] vs .iloc[]
# ------------------------------------
# - THE single most important distinction in pandas:
#   .loc[]  -> LABEL-based: selects by index/column LABEL. Slices are
#              INCLUSIVE of the end label.
#   .iloc[] -> POSITION-based: selects by integer POSITION, exactly like
#              Python list/array slicing. Slices EXCLUDE the end position.
# - Since `orders` has labels 'a'..'e' (not 0..4), the difference is stark.

print("\n# 02. .loc[] (label-based) vs .iloc[] (position-based)")
print("# ------------------------------------")

print("orders.loc['b'] (row labeled 'b'):\n", orders.loc["b"], sep="")
print("\norders.iloc[1] (row at position 1 -> same row here, different mechanism):\n", orders.iloc[1], sep="")

print("\norders.loc['a':'c'] (label slice, INCLUSIVE of 'c'):\n", orders.loc["a":"c"], sep="")
print("\norders.iloc[0:2] (position slice, EXCLUDES index 2):\n", orders.iloc[0:2], sep="")
print("# Same starting point, different row counts: loc gave 3 rows, iloc gave 2 - inclusive vs exclusive.")

print("\norders.loc['b', 'amount'] (label row, label column) =", orders.loc["b", "amount"])
print("orders.iloc[1, 2] (position row, position column)    =", orders.iloc[1, 2])

print("\norders.loc[:, ['customer', 'status']] (all rows, label-selected columns):\n", orders.loc[:, ["customer", "status"]], sep="")
print("\norders.iloc[:, [1, 3]] (all rows, position-selected columns, same result here):\n", orders.iloc[:, [1, 3]], sep="")

print("\n# Gotcha: if the index were integers (e.g. default RangeIndex), df.loc[0:2] and df.iloc[0:2]")
print("#   would look similar but still differ - loc treats 0..2 as LABELS (inclusive), iloc as")
print("#   POSITIONS (exclusive of 2). Never assume they're interchangeable just because both take ints.")

# 03. .at[] / .iat[] for Fast Scalar Access
# ------------------------------------
# - .at[row_label, col_label]   -> label-based, single scalar only.
# - .iat[row_pos, col_pos]      -> position-based, single scalar only.
# - Faster than .loc/.iloc for a single value because they skip the
#   generalized indexing machinery built for slices/arrays/lists.

print("\n# 03. .at[] / .iat[] for Fast Scalar Access")
print("# ------------------------------------")

print("orders.at['c', 'amount']  =", orders.at["c", "amount"])
print("orders.iat[2, 2]          =", orders.iat[2, 2], "(same cell, position-based)")
print("# Use .at/.iat when you need ONE cell in a hot loop; use .loc/.iloc for slices/arrays/lists.")

# 04. Boolean / Mask Filtering
# ------------------------------------
# - df['col'] > value produces a boolean Series (the "mask"); df[mask]
#   keeps only the rows where the mask is True. This is THE standard way
#   to filter rows in pandas.

print("\n# 04. Boolean / Mask Filtering")
print("# ------------------------------------")

mask = orders["amount"] > 200
print("mask = orders['amount'] > 200:\n", mask, sep="")
print("\norders[mask] (rows where amount > 200):\n", orders[mask], sep="")
print("\nShorthand, same result: orders[orders['amount'] > 200]")

# 05. Combining Conditions with & / |
# ------------------------------------
# - Use & (and), | (or), ~ (not) - NOT the Python keywords 'and'/'or'.
# - Python's 'and'/'or' call bool() on their operands, but a Series with
#   more than one element has an AMBIGUOUS truth value -> ValueError.
#   &/|/~ are overloaded to do ELEMENTWISE boolean logic instead, like NumPy.
# - Each condition MUST be wrapped in parentheses because & has higher
#   operator precedence than comparison operators in Python.

print("\n# 05. Combining Conditions with & / | (and why 'and'/'or' fail)")
print("# ------------------------------------")

combo = orders[(orders["amount"] > 100) & (orders["status"] == "shipped")]
print("orders[(amount > 100) & (status == 'shipped')]:\n", combo, sep="")

either = orders[(orders["status"] == "cancelled") | (orders["amount"] > 900)]
print("\norders[(status == 'cancelled') | (amount > 900)]:\n", either, sep="")

not_shipped = orders[~(orders["status"] == "shipped")]
print("\norders[~(status == 'shipped')] (negation with ~):\n", not_shipped, sep="")

try:
    orders[(orders["amount"] > 100) and (orders["status"] == "shipped")]
except ValueError as e:
    print("\nUsing Python 'and' instead of '&' raises ValueError:", e)

# 06. The SettingWithCopyWarning Gotcha
# ------------------------------------
# - df[mask]['col'] = value is CHAINED indexing: first df[mask] creates a
#   NEW object (which may be a view OR a copy - pandas doesn't guarantee
#   which), then ['col'] = value assigns onto that intermediate object.
#   pandas can't reliably tell if the assignment reached the original
#   DataFrame, so it raises SettingWithCopyWarning - the edit might be lost.
# - The fix: do the row selection and column assignment in ONE .loc[] call,
#   df.loc[mask, 'col'] = value, which pandas can resolve unambiguously
#   against the original DataFrame.

print("\n# 06. The SettingWithCopyWarning Gotcha")
print("# ------------------------------------")

orders_copy = orders.copy()
print("WRONG (chained indexing) - triggers SettingWithCopyWarning, may silently not update orders_copy:")
print("    orders_copy[orders_copy['status'] == 'pending']['amount'] = 0")
print("# (not executed here - it's an anti-pattern, shown for reference only)")

print("\nCORRECT - single .loc[] call, row mask + column label together:")
orders_copy.loc[orders_copy["status"] == "pending", "amount"] = 0
print(orders_copy)
print("# .loc[mask, 'col'] = value updates orders_copy directly and unambiguously - no warning.")

print("\n# End of Selection and Indexing")
