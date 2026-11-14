# Reshaping — Notes

## What this covers
The wide-vs-long mental model behind every reshape operation, then the four tools that convert between them: `.pivot()`, `.pivot_table()`, `.melt()`, and `.stack()`/`.unstack()`.

## Key points
- **Wide**: one row per entity, each variable is its own column (easy to read). **Long**: one row per (entity, variable, value) triple (easy to filter/group/plot). Every reshape function just converts between these two shapes.
- `.pivot(index=, columns=, values=)` — long to wide, no aggregation. Requires each `(index, columns)` pair to be unique; if a pair repeats, it raises `ValueError: Index contains duplicate entries, cannot reshape`.
- `.pivot_table(index=, columns=, values=, aggfunc=)` — same shape change, but aggregates when an `(index, columns)` pair repeats (default `aggfunc='mean'`). Effectively `groupby(index + columns)` followed by a reshape into a grid.
- `.melt(id_vars=, value_vars=, var_name=, value_name=)` — wide to long. `id_vars` are the columns kept as-is; `value_vars` are the columns collapsed into `variable`/`value` pairs (defaults to every non-`id_vars` column).
- `.stack()` / `.unstack()` do the same wide<->long conversion but operate on **index/column levels directly** (MultiIndex), not on named column arguments — `.stack()` moves the innermost column level into the row index; `.unstack()` moves it back out.
- `melt()` and `pivot()` are inverses: wide -> melt -> pivot recovers the original data (column order may need restoring since pivot alphabetizes columns).

## Gotchas (the part worth revising twice)
- Reaching for `.pivot()` on data with duplicate `(index, columns)` pairs is the single most common reshape error — it fails loudly instead of silently guessing, which is the correct behavior; switch to `.pivot_table()` with an explicit `aggfunc` once duplicates exist.
- `.pivot_table()` defaults to `aggfunc='mean'`, which silently changes your numbers if you actually wanted `'sum'`, `'max'`, or `'count'` — always set `aggfunc` explicitly for anything beyond quick exploration.
- After `pivot()`/`pivot_table()`, the result's columns carry a leftover "columns axis name" (e.g. `subject`) and the original row identifier becomes the index, not a column — `reset_index()` and `columns.name = None` if you need a plain flat DataFrame again.
- `.stack()` on a DataFrame returns a **Series** with a MultiIndex, not a DataFrame — easy to forget when chaining further operations.

## When it matters
Data rarely arrives in the shape a specific tool needs: plotting libraries and `groupby` generally want long format, while reports and pivot-style summaries want wide format — reshaping is the everyday bridge between "how the data was collected" and "how it needs to be viewed."

## One-line recap example
```python
import pandas as pd
long_df = wide_df.melt(id_vars="student", var_name="subject", value_name="score")
back_to_wide = long_df.pivot(index="student", columns="subject", values="score")
```
