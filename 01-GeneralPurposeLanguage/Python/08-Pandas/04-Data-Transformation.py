# 01. .apply() - Row-wise vs Column-wise (axis=)
# 02. .map() - Series-only Element-wise Substitution/Lookup
# 03. Vectorized-Operation-First Principle (timing: vectorized vs .apply)
# 04. .sort_values() / .sort_index()
# 05. .value_counts(), .unique(), .nunique()
# 06. .replace()

import pandas as pd
import numpy as np
import time

sales = pd.DataFrame({
    "product": ["Widget", "Gadget", "Widget", "Gizmo", "Gadget", "Widget"],
    "region": ["East", "West", "East", "West", "East", "West"],
    "units": [120, 45, 80, 30, 60, 95],
    "unit_price": [9.99, 24.50, 9.99, 15.00, 24.50, 9.99],
})
print("sales:\n", sales, sep="")

# 01. .apply() - Row-wise vs Column-wise
# ------------------------------------
# - Series.apply(func)     -> calls func on each ELEMENT.
# - DataFrame.apply(func, axis=0) (default) -> calls func on each COLUMN
#   (a Series representing that column) - good for per-column reductions.
# - DataFrame.apply(func, axis=1) -> calls func on each ROW (a Series
#   representing that row) - good when a computation needs MULTIPLE
#   columns together, which a single-column vectorized op can't express.

print("\n# 01. .apply() - Row-wise vs Column-wise")
print("# ------------------------------------")

print("sales['units'].apply(lambda x: x * 2) (Series.apply, element-wise):")
print(sales["units"].apply(lambda x: x * 2).tolist())

col_ranges = sales[["units", "unit_price"]].apply(lambda col: col.max() - col.min(), axis=0)
print("\nDataFrame.apply(axis=0) - per-COLUMN range (max-min) of units & unit_price:")
print(col_ranges)

row_totals = sales.apply(lambda row: row["units"] * row["unit_price"], axis=1)
print("\nDataFrame.apply(axis=1) - per-ROW total (units * unit_price, needs 2 columns together):")
print(row_totals.tolist())

# 02. .map() - Series-only Element-wise Substitution/Lookup
# ------------------------------------
# - .map() exists ONLY on a Series (not a DataFrame). It substitutes each
#   value using a dict, another Series, or a function - a lookup/translation
#   tool, distinct from .apply()'s more general "call this function" role.
# - Values not found in a dict/Series mapping become NaN.

print("\n# 02. .map() - Series-only Element-wise Substitution/Lookup")
print("# ------------------------------------")

category_lookup = {"Widget": "Hardware", "Gadget": "Electronics", "Gizmo": "Electronics"}
print("sales['product'].map(category_lookup) (dict lookup):")
print(sales["product"].map(category_lookup).tolist())

region_short = sales["region"].map(lambda r: r[0])
print("\nsales['region'].map(lambda r: r[0]) (function, first letter):", region_short.tolist())

unknown_lookup = {"Widget": "Hardware"}  # Gadget/Gizmo intentionally missing
print("\nsales['product'].map({'Widget': 'Hardware'}) (missing keys -> NaN):")
print(sales["product"].map(unknown_lookup).tolist())

# 03. Vectorized-Operation-First Principle
# ------------------------------------
# - Pandas/NumPy vectorized ops run in compiled C loops over contiguous
#   memory. .apply() (and worse, a raw Python for-loop) calls a Python
#   function once per row/element - Python function-call overhead dominates,
#   and it's usually 10-100x slower on realistic data sizes.
# - Reach for .apply() only when the operation truly can't be expressed as
#   vectorized arithmetic/boolean logic/built-in Series methods.

print("\n# 03. Vectorized-Operation-First Principle")
print("# ------------------------------------")

big = pd.DataFrame({"a": np.random.rand(200_000), "b": np.random.rand(200_000)})

start = time.perf_counter()
vectorized_result = big["a"] * big["b"]
vectorized_time = time.perf_counter() - start

start = time.perf_counter()
apply_result = big.apply(lambda row: row["a"] * row["b"], axis=1)
apply_time = time.perf_counter() - start

print(f"Same computation (a * b) over {len(big):,} rows:")
print(f"  vectorized (big['a'] * big['b'])      : {vectorized_time:.4f}s")
print(f"  .apply(axis=1) (Python call per row)  : {apply_time:.4f}s")
print(f"  .apply() was ~{apply_time / max(vectorized_time, 1e-9):.0f}x slower")
print("# Rule of thumb: if it's arithmetic, a comparison, or has a vectorized/Series method")
print("#   equivalent (.str, .dt, np.where, ...), do NOT reach for .apply() first.")

# 04. .sort_values() / .sort_index()
# ------------------------------------
# - .sort_values(by=col_or_list, ascending=True/False) sorts rows by value(s).
# - .sort_index() sorts rows by their index label instead of any column.

print("\n# 04. .sort_values() / .sort_index()")
print("# ------------------------------------")

print("sales.sort_values('units', ascending=False):")
print(sales.sort_values("units", ascending=False))

print("\nsales.sort_values(['region', 'units']) (multi-column sort):")
print(sales.sort_values(["region", "units"]))

shuffled_index = sales.sample(frac=1, random_state=42)
print("\nshuffled_index.sort_index() (restores original row order by index label):")
print(shuffled_index.sort_index())

# 05. .value_counts(), .unique(), .nunique()
# ------------------------------------
# - .value_counts() -> counts of each distinct value, sorted descending by
#   default - the fastest way to see a column's distribution.
# - .unique() -> array of distinct values, in order of first appearance.
# - .nunique() -> count of distinct values (a single number).

print("\n# 05. .value_counts(), .unique(), .nunique()")
print("# ------------------------------------")

print("sales['product'].value_counts():\n", sales["product"].value_counts(), sep="")
print("\nsales['product'].unique() =", sales["product"].unique())
print("sales['product'].nunique() =", sales["product"].nunique())
print("sales['product'].value_counts(normalize=True) (proportions instead of counts):")
print(sales["product"].value_counts(normalize=True))

# 06. .replace()
# ------------------------------------
# - .replace(old, new) swaps specific values for new ones - works with a
#   single old->new pair, a dict of many pairs, or per-column dicts - unlike
#   .map(), unmatched values are left UNCHANGED rather than becoming NaN.

print("\n# 06. .replace()")
print("# ------------------------------------")

print("sales['region'].replace({'East': 'EAST', 'West': 'WEST'}):")
print(sales["region"].replace({"East": "EAST", "West": "WEST"}).tolist())
print("\n# Contrast with .map(): .replace() leaves values NOT in the dict untouched,")
print("#   .map() turns values NOT in the dict/Series into NaN.")

print("\n# End of Data Transformation")
