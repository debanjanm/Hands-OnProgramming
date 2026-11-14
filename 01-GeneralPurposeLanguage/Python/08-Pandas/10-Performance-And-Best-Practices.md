# Performance and Best Practices — Notes

## What this covers
Why vectorized operations dominate `.apply()` and `.iterrows()`, how to shrink DataFrame memory with `category` dtype and integer downcasting, readable method chaining with `.pipe()`/`.query()`/`.assign()`, and the `copy()` vs view distinction behind `SettingWithCopyWarning`.

## Key points
- Same row-wise computation, three ways, on 50,000 rows: vectorized arithmetic was ~500x faster than `.apply(axis=1)` and ~1700x faster than a manual `.iterrows()` loop in this run (exact multiples vary by machine, direction never does).
- Vectorized ops run in compiled C loops; `.apply(axis=1)` still calls a Python function once per row — it *looks* vectorized syntactically but isn't; `.iterrows()` is worst because it reconstructs a full Series object for every row.
- `.memory_usage(deep=False)` (the default) undercounts `object` (string) columns — it only measures the pointer array, not the string data itself. `.memory_usage(deep=True)` walks into the actual objects for the real footprint.
- Converting a low-cardinality `object` column to `category` dtype stores one small integer code per row plus a shared lookup table of distinct values — a big memory win when distinct values are few relative to row count, a net loss on high-cardinality columns (e.g. unique IDs).
- `pd.to_numeric(series, downcast="integer")` picks the smallest integer dtype (e.g. `int8`) that still holds every value without overflow, instead of the default `int64`.
- Method chaining (`.query().pipe().sort_values()...`) reads as one linear pipeline and avoids throwaway intermediate variable names; `.pipe(func)` lets a plain function slot into the chain. Trade-off: harder to set a breakpoint mid-chain when debugging.
- `.query("expr")` filters with a string expression (reads like SQL `WHERE`); `.eval("expr")` computes a new column/expression the same way — both avoid repeating the DataFrame's name inside boolean-mask expressions.
- Slicing a DataFrame may return a view or a copy — pandas doesn't guarantee which. Mutating an ambiguous result raises `SettingWithCopyWarning` (a warning, not an exception — execution continues). Calling `.copy()` explicitly the moment you intend to keep modifying a filtered result removes the ambiguity entirely.

## Gotchas (the part worth revising twice)
- `.apply(axis=1)` is a common "I vectorized it" false positive — it's still a Python-level loop under the hood, just hidden behind pandas syntax.
- `SettingWithCopyWarning` is only a warning by default — code that triggers it keeps running and can produce silently wrong results (the original frame not actually updated) rather than crashing where you'd notice.
- `category` dtype is not a universal win — applying it to a high-cardinality column (e.g. an email address per row) adds overhead without the memory benefit, since there's no meaningful repetition to compress.
- `pd.to_numeric(downcast=...)` returns a *new* Series — it doesn't mutate in place; the result must be reassigned.

## When it matters
Any script processing more than a few thousand rows benefits from checking whether an operation is truly vectorized — the difference between vectorized and `.iterrows()` compounds fast and is one of the most common reasons a "slow pandas script" turns out to be an easy fix; memory-dtype tuning matters most on wide, mixed-type DataFrames loaded from CSV/database exports.

## One-line recap example
```python
import pandas as pd
df["total"] = df["price"] * df["quantity"]          # vectorized, not df.apply(...) or a loop
df["dept"] = df["dept"].astype("category")           # shrink a low-cardinality column
```
