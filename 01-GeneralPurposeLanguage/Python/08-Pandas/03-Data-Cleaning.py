# 01. Missing Data: .isna() / .notna()
# 02. Filling Missing Data: .fillna() (scalar, ffill, bfill)
# 03. Dropping Missing Data: .dropna() (axis, how, subset)
# 04. Duplicates: .duplicated() / .drop_duplicates()
# 05. Type Conversion: .astype() and the object-column gotcha
# 06. The .str Accessor for Vectorized String Ops
# 07. Renaming Columns: .rename()

import pandas as pd
import numpy as np

customers = pd.DataFrame({
    "customer_id": [1, 2, 3, 4, 5, 5],
    "name": [" Alice ", "bob", "CARLA", "Dev", "eve", "eve"],
    "email": ["alice@mail.com", None, "carla@mail.com", "dev@mail.com", "eve@mail.com", "eve@mail.com"],
    "age": [34, np.nan, 29, 41, np.nan, np.nan],
    "signup_date": ["2023-01-15", "2023-02-20", None, "2023-03-05", "2023-04-01", "2023-04-01"],
})
print("customers:\n", customers, sep="")

# 01. Missing Data: .isna() / .notna()
# ------------------------------------
# - .isna() (alias .isnull()) returns a same-shape boolean DataFrame/Series,
#   True where a value is NaN/None/NaT. .notna() is the exact inverse.
# - .isna().sum() is the standard one-liner for a per-column missing count.

print("\n# 01. Missing Data: .isna() / .notna()")
print("# ------------------------------------")

print("customers.isna():\n", customers.isna(), sep="")
print("\nMissing values per column - customers.isna().sum():\n", customers.isna().sum(), sep="")
print("\ncustomers['age'].notna() (inverse mask):\n", customers["age"].notna(), sep="")

# 02. Filling Missing Data: .fillna()
# ------------------------------------
# - .fillna(value) fills every NaN with a scalar (or a per-column dict of
#   scalars).
# - method='ffill' (forward-fill) propagates the last valid value forward;
#   method='bfill' (back-fill) propagates the next valid value backward -
#   useful for time-ordered data where a missing reading likely equals its
#   neighbor.

print("\n# 02. Filling Missing Data: .fillna()")
print("# ------------------------------------")

print("Fill 'age' NaNs with the column mean:")
print(customers["age"].fillna(customers["age"].mean()))

print("\nFill per-column with a dict {'age': 0, 'email': 'unknown'}:")
print(customers.fillna({"age": 0, "email": "unknown"})[["age", "email"]])

ordered = pd.Series([1.0, np.nan, np.nan, 4.0, np.nan])
print("\nordered =", list(ordered))
print("ordered.fillna(method='ffill') =", list(ordered.ffill()), "(each NaN takes the last value BEFORE it)")
print("ordered.fillna(method='bfill') =", list(ordered.bfill()), "(each NaN takes the next value AFTER it)")
print("# Note: .ffill()/.bfill() are the modern spelling; fillna(method='ffill') still works but is")
print("#   deprecated in favor of calling .ffill()/.bfill() directly.")

# 03. Dropping Missing Data: .dropna()
# ------------------------------------
# - axis=0 (default) drops ROWS containing NaN; axis=1 drops COLUMNS.
# - how='any' (default) drops if ANY value in the row/column is NaN;
#   how='all' drops only if EVERY value is NaN.
# - subset=[...] restricts the NaN check to specific columns only.

print("\n# 03. Dropping Missing Data: .dropna()")
print("# ------------------------------------")

print("customers.dropna() (default: drop any row with ANY NaN):\n", customers.dropna(), sep="")
print("\ncustomers.dropna(subset=['email']) (only check the 'email' column):\n", customers.dropna(subset=["email"]), sep="")
print("\ncustomers.dropna(how='all') (only drop rows that are ENTIRELY NaN - none here):\n", customers.dropna(how="all").shape, "rows unchanged")

# 04. Duplicates: .duplicated() / .drop_duplicates()
# ------------------------------------
# - .duplicated() flags rows that are exact repeats of an EARLIER row
#   (keep='first' by default -> first occurrence is False, later repeats True).
# - .drop_duplicates() removes those repeats; subset=[...] limits which
#   columns count toward "duplicate", keep='last'/False change which
#   occurrence(s) survive.

print("\n# 04. Duplicates: .duplicated() / .drop_duplicates()")
print("# ------------------------------------")

print("customers.duplicated() (True where the ENTIRE row repeats an earlier one):\n", customers.duplicated(), sep="")
print("\ncustomers.duplicated(subset=['customer_id']) (duplicate check on just customer_id):\n", customers.duplicated(subset=["customer_id"]), sep="")
print("\ncustomers.drop_duplicates(subset=['customer_id'], keep='first'):\n", customers.drop_duplicates(subset=["customer_id"], keep="first"), sep="")

# 05. Type Conversion: .astype() and the object-column gotcha
# ------------------------------------
# - .astype(dtype) converts a column/Series to a new dtype, returns a NEW
#   object (doesn't mutate in place unless reassigned).
# - Classic gotcha: a numeric column read from messy data (CSV, user input)
#   becomes dtype 'object' the moment ONE value isn't a clean number (e.g. a
#   stray "N/A" string) - pandas can't store mixed str/int in a numeric dtype,
#   so it falls back to Python objects for the whole column.
# - pd.to_numeric(series, errors='coerce') is the fix: it converts what it
#   can and turns anything unparseable into NaN instead of raising/silently
#   staying object dtype.

print("\n# 05. Type Conversion: .astype() and the object-column gotcha")
print("# ------------------------------------")

clean_prices = pd.Series(["19.99", "5.50", "120.00"])
print("clean_prices dtype before:", clean_prices.dtype)
print("clean_prices.astype(float) dtype after:", clean_prices.astype(float).dtype)

messy_prices = pd.Series(["19.99", "5.50", "N/A", "12.00"])
print("\nmessy_prices =", list(messy_prices), "dtype:", messy_prices.dtype, "(object - looks numeric but isn't)")
try:
    messy_prices.astype(float)
except ValueError as e:
    print("messy_prices.astype(float) raises ValueError:", e)

coerced = pd.to_numeric(messy_prices, errors="coerce")
print("pd.to_numeric(messy_prices, errors='coerce'):\n", coerced, sep="")
print("# 'N/A' -> NaN instead of raising; now you can .fillna()/.dropna() it like any missing value.")

# 06. The .str Accessor for Vectorized String Ops
# ------------------------------------
# - .str gives vectorized, NaN-safe string methods on an object/string
#   Series - equivalent to Python str methods but applied to every element
#   at once, no explicit loop or .apply(lambda s: s.upper()) needed.

print("\n# 06. The .str Accessor for Vectorized String Ops")
print("# ------------------------------------")

print("customers['name'] raw:", list(customers["name"]))
print("customers['name'].str.strip().str.upper():", list(customers["name"].str.strip().str.upper()))
print("customers['email'].str.contains('mail.com', na=False):", list(customers["email"].str.contains("mail.com", na=False)))
print("(na=False treats NaN as 'no match' instead of propagating NaN into the boolean mask)")
print("customers['signup_date'].str.split('-').iloc[0] ->", customers["signup_date"].str.split("-").iloc[0], "(splits into a list per row)")

# 07. Renaming Columns: .rename()
# ------------------------------------
# - .rename(columns={...}) renames specific columns by old->new name mapping,
#   leaving the rest untouched - safer than reassigning .columns wholesale
#   when you only want to fix a few names.

print("\n# 07. Renaming Columns: .rename()")
print("# ------------------------------------")

renamed = customers.rename(columns={"customer_id": "id", "signup_date": "joined_on"})
print("customers.rename(columns={'customer_id': 'id', 'signup_date': 'joined_on'}):")
print(renamed.columns.tolist())

print("\n# End of Data Cleaning")
