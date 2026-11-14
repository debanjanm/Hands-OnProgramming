# 01. Vectorized Ops vs .apply() vs .iterrows() - Timing Comparison
# 02. Memory Optimization with .memory_usage(deep=True)
# 03. category dtype for Low-Cardinality Columns
# 04. Integer Downcasting with pd.to_numeric(downcast='integer')
# 05. Method Chaining - .pipe() / .query() / .assign() / .sort_values()
# 06. .query() and .eval() for Readable/Faster Filtering
# 07. df.copy() vs View Semantics - SettingWithCopyWarning Recap

import pandas as pd
import numpy as np
import time
import warnings

# 01. Vectorized Ops vs .apply() vs .iterrows() - Timing Comparison
# ------------------------------------
# - Same row-wise computation done three ways on a 50,000-row frame:
#   vectorized arithmetic, .apply(axis=1) with a Python function, and a
#   manual .iterrows() loop. All three compute the identical result
#   (price * quantity * (1 - discount)); only the mechanism differs.

print("# 01. Vectorized Ops vs .apply() vs .iterrows() - Timing Comparison")
print("# ------------------------------------")

rng = np.random.default_rng(0)
n = 50_000
big = pd.DataFrame({
    "price": rng.uniform(5, 500, size=n),
    "quantity": rng.integers(1, 20, size=n),
    "discount": rng.uniform(0, 0.3, size=n),
})
print(f"Test frame: {n:,} rows. Computing total = price * quantity * (1 - discount) three ways.\n")

start = time.perf_counter()
vectorized_result = big["price"] * big["quantity"] * (1 - big["discount"])
vectorized_time = time.perf_counter() - start
print(f"Vectorized (arithmetic on whole Series):  {vectorized_time:.5f}s")

start = time.perf_counter()
apply_result = big.apply(lambda row: row["price"] * row["quantity"] * (1 - row["discount"]), axis=1)
apply_time = time.perf_counter() - start
print(f".apply(axis=1) (Python function per row): {apply_time:.5f}s")

start = time.perf_counter()
iterrows_result = pd.Series(
    [row["price"] * row["quantity"] * (1 - row["discount"]) for _, row in big.iterrows()],
    index=big.index,
)
iterrows_time = time.perf_counter() - start
print(f".iterrows() (manual Python loop):         {iterrows_time:.5f}s")

print(f"\nAll three produce the same result: "
      f"{np.allclose(vectorized_result, apply_result) and np.allclose(vectorized_result, iterrows_result)}")
print(f"apply() is ~{apply_time / vectorized_time:.0f}x slower than vectorized;",
      f"iterrows() is ~{iterrows_time / vectorized_time:.0f}x slower than vectorized.")
print("# Vectorized ops call compiled C loops under the hood, same reason NumPy beats manual")
print("#   Python loops. apply(axis=1) still runs a Python function per row - it looks vectorized")
print("#   but isn't. iterrows() is worst: it rebuilds a Series object for every single row.")

# 02. Memory Optimization with .memory_usage(deep=True)
# ------------------------------------
# - .memory_usage() reports bytes per column. For object (string) columns,
#   the DEFAULT undercounts badly - it only measures the pointer array, not
#   the actual string objects. deep=True walks into each object and measures
#   the real memory footprint.

print("\n# 02. Memory Optimization with .memory_usage(deep=True)")
print("# ------------------------------------")

employees = pd.DataFrame({
    "emp_id": range(10_000),
    "department": rng.choice(["Engineering", "Sales", "Marketing", "Legal", "HR"], size=10_000),
    "status": rng.choice(["Active", "Inactive"], size=10_000),
})

shallow = employees.memory_usage(deep=False).sum()
deep = employees.memory_usage(deep=True).sum()
print(f"memory_usage(deep=False).sum() = {shallow:,} bytes  (undercounts object columns)")
print(f"memory_usage(deep=True).sum()  = {deep:,} bytes  (real footprint, walks into string data)")
print(f"Deep usage is {deep / shallow:.1f}x the shallow number - the gap IS the string data.")

# 03. category dtype for Low-Cardinality Columns
# ------------------------------------
# - 'department' only has 5 distinct values across 10,000 rows - a classic
#   LOW-CARDINALITY column. Storing it as 'category' keeps one small integer
#   code per row plus a shared lookup table of the distinct strings, instead
#   of a separate Python string object per row.

print("\n# 03. category dtype for Low-Cardinality Columns")
print("# ------------------------------------")

print("department distinct values:", employees["department"].nunique(), "across", len(employees), "rows")

before_bytes = employees["department"].memory_usage(deep=True)
employees["department"] = employees["department"].astype("category")
after_bytes = employees["department"].memory_usage(deep=True)
print(f"'department' as object:   {before_bytes:,} bytes")
print(f"'department' as category: {after_bytes:,} bytes  ({after_bytes / before_bytes:.1%} of original)")
print("# category dtype pays off precisely when distinct-value count is small relative to row")
print("#   count - it would be a net LOSS on a high-cardinality column like a unique email address.")

# 04. Integer Downcasting with pd.to_numeric(downcast='integer')
# ------------------------------------
# - Plain int columns default to int64 even when the actual values fit in a
#   much smaller type. downcast='integer' picks the smallest int dtype that
#   still holds every value without overflow.

print("\n# 04. Integer Downcasting with pd.to_numeric(downcast='integer')")
print("# ------------------------------------")

ages = pd.Series(rng.integers(18, 70, size=10_000))
print("ages dtype (default):", ages.dtype, "-", ages.memory_usage(deep=True), "bytes")

ages_downcast = pd.to_numeric(ages, downcast="integer")
print("ages dtype (downcast='integer'):", ages_downcast.dtype, "-",
      ages_downcast.memory_usage(deep=True), "bytes")
print("# Values only range 18-70, which fits comfortably in int8 (-128..127) -")
print("#   pandas picks the smallest safe type automatically, no manual bit-width math needed.")

# 05. Method Chaining - .pipe() / .query() / .assign() / .sort_values()
# ------------------------------------
# - Step-by-step reassignment (df = df[...]; df = df.assign(...); ...)
#   creates intermediate variables and is easy to get out of order.
# - Chaining reads top-to-bottom as one pipeline; .pipe() lets you drop a
#   plain function into the chain instead of breaking out of it.

print("\n# 05. Method Chaining - .pipe() / .query() / .assign() / .sort_values()")
print("# ------------------------------------")

def add_total_column(df):
    """A plain function - .pipe() lets it slot into a method chain."""
    return df.assign(total=df["price"] * df["quantity"])

# Step-by-step version (equivalent result, more intermediate names to track).
step1 = big.copy()
step2 = step1[step1["quantity"] > 10]
step3 = step2.assign(total=step2["price"] * step2["quantity"])
step_by_step_result = step3.sort_values("total", ascending=False).head(3)

# Chained version - same logic, reads as one pipeline.
chained_result = (
    big
    .query("quantity > 10")
    .pipe(add_total_column)
    .sort_values("total", ascending=False)
    .head(3)
)

print("Step-by-step result:\n", step_by_step_result[["price", "quantity", "total"]])
print("\nChained result (same logic via .query()/.pipe()/.sort_values()):\n",
      chained_result[["price", "quantity", "total"]])
print("Results match:", step_by_step_result[["price", "quantity", "total"]].equals(
    chained_result[["price", "quantity", "total"]]))
print("# Chaining avoids throwaway intermediate variable names (step1, step2...) - trade-off is")
print("#   harder to set a breakpoint mid-chain when debugging; split it back out temporarily if needed.")

# 06. .query() and .eval() for Readable/Faster Filtering
# ------------------------------------
# - .query("expr") filters rows using a string expression instead of boolean
#   masks - reads closer to SQL WHERE, and for large frames can be faster
#   because it uses the numexpr engine (if installed) to avoid building full
#   intermediate boolean arrays in Python.
# - .eval("expr") does the same for computing a new column/expression.

print("\n# 06. .query() and .eval() for Readable/Faster Filtering")
print("# ------------------------------------")

mask_style = big[(big["quantity"] > 15) & (big["price"] < 50)]
query_style = big.query("quantity > 15 and price < 50")
print("Boolean-mask filter rows:", len(mask_style), "| .query() filter rows:", len(query_style))
print("Same result:", mask_style.equals(query_style))

eval_result = big.eval("total = price * quantity * (1 - discount)")
print("\n.eval() adds a computed column via a string expression, head(3):\n",
      eval_result[["price", "quantity", "discount", "total"]].head(3))
print("# .query()/.eval() read like SQL/spreadsheet formulas and avoid writing")
print("#   big[(big['quantity'] > 15) & (big['price'] < 50)] with repeated frame-name references.")

# 07. df.copy() vs View Semantics - SettingWithCopyWarning Recap
# ------------------------------------
# - Slicing a DataFrame (e.g. df[df['x'] > 5]) MAY return a view or a copy -
#   pandas doesn't guarantee which, and mutating the result raises
#   SettingWithCopyWarning (a warning, not an exception - execution continues,
#   which is exactly why it's dangerous: easy to miss in a noisy log).
# - The fix is always the same: call .copy() explicitly the moment you intend
#   to keep modifying a filtered/sliced result independently of the original.

print("\n# 07. df.copy() vs View Semantics - SettingWithCopyWarning Recap")
print("# ------------------------------------")

subset_no_copy = big[big["quantity"] > 15]
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    subset_no_copy["flag"] = True  # ambiguous: view or copy of `big`? pandas warns, doesn't stop.
    if caught:
        print("Assignment triggered:", caught[0].category.__name__)
        first_line = next(line for line in str(caught[0].message).splitlines() if line.strip())
        print("Message (truncated):", first_line)

subset_with_copy = big[big["quantity"] > 15].copy()
subset_with_copy["flag"] = True  # safe: subset_with_copy is unambiguously independent
print("subset_with_copy['flag'] set cleanly after .copy() - no warning, no ambiguity.")
print("'flag' in original big.columns:", "flag" in big.columns, "(original untouched either way)")
print("# Rule of thumb: the instant you plan to mutate a filtered/sliced result, call .copy()")
print("#   right there - don't wait to find out the hard way whether pandas handed you a view.")

print("\n# End of Performance and Best Practices")
