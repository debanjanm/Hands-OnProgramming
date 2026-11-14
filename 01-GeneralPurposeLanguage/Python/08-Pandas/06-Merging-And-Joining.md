# Merging and Joining — Notes

## What this covers
How to combine two DataFrames with `pd.merge()` (SQL-style JOIN on a key column), `.join()` (index-based merging), and `pd.concat()` (stacking frames by position/index rather than matching keys).

## Key points
- `pd.merge(left, right, on=key, how=...)` — `how` controls which unmatched rows survive: `'inner'` (matches only), `'left'` (all left rows), `'right'` (all right rows), `'outer'` (union of both). Unmatched cells become `NaN`.
- `on=[col1, col2]` merges on multiple keys together — all listed columns must match, not just one.
- When both frames share a non-key column name, pandas appends `suffixes=` (default `('_x', '_y')`) to tell them apart; pass a custom tuple for readable output.
- `.join()` merges on the **index** by default (`how='left'` by default) — natural when the key already lives in the index; `pd.merge()` defaults to `how='inner'` on shared column names.
- `pd.concat([a, b], axis=0)` stacks rows (like SQL `UNION ALL`), matching columns by name; `axis=1` stacks columns side by side, aligning by **index label**.
- `pd.concat(axis=0)` keeps the original index from each frame by default (can produce duplicate index labels) — pass `ignore_index=True` for a fresh `0..n-1` index.

## Gotchas (the part worth revising twice)
- `pd.concat(axis=1)` with mismatched indices does NOT raise an error — it silently NaN-pads every row whose index label doesn't exist on the other side. `reset_index(drop=True)` first if you want purely positional pairing.
- `how='right'` and `how='outer'` can upcast an integer key/ID column to float (e.g. `1` becomes `1.0`) because the unmatched rows introduce `NaN`, and a column with any `NaN` can't stay integer dtype.
- Default merge suffixes `_x`/`_y` are easy to mix up in wide output — always pass explicit `suffixes=` once a script has more than one overlapping column.
- `.join()` and `.merge()` are not fully interchangeable: `.join()` needs `on=` to join on a column instead of the index, while `.merge()` needs `left_index=True`/`right_index=True` to join on the index.

## When it matters
Combining tables from different sources (a transactions file and a customer lookup table, two API responses, a day's data appended to history) is one of the most common real-world data prep steps — picking the wrong `how=` silently drops or duplicates rows.

## One-line recap example
```python
import pandas as pd
merged = pd.merge(employees, departments, on="dept_id", how="left")  # keep every employee, NaN if no dept match
```
