# Series and DataFrame Basics — Notes

## What this covers
How to build a pandas `Series` (1D labeled array) and a `DataFrame` (2D labeled table) from various sources, the core attributes for inspecting one, and how a DataFrame relates to its columns underneath.

## Key points
- `pd.Series(list)` gets a default `RangeIndex`; `pd.Series(dict)` uses dict keys as the index; `index=` sets a custom one.
- `pd.DataFrame(dict_of_lists)` maps dict keys to column names; `pd.DataFrame(list_of_dicts)` maps each dict to one row (missing keys become `NaN`); `pd.DataFrame(ndarray, columns=..., index=...)` is needed for raw arrays since they carry no labels.
- `.shape`, `.columns`, `.index` mirror NumPy conventions but with labels instead of just positions.
- `.dtypes` is per-column — unlike a NumPy array's single shared dtype, every DataFrame column can have its own.
- `.values` drops all labels and returns a plain NumPy array; mixed-dtype columns upcast to a common dtype (often `object`).
- `.info()` shows dtypes, non-null counts, and memory — the first command to run on any unfamiliar DataFrame.
- `.describe()` summarizes numeric columns by default (count/mean/std/quartiles); `include='all'` adds `unique`/`top`/`freq` for object columns too.
- `.head(n)` / `.tail(n)` (default `n=5`) preview a large table.
- A DataFrame is essentially a dict-like collection of Series that all share the same row index — `df['col']` returns a real Series view aligned to that shared index, not disconnected data.

## Gotchas (the part worth revising twice)
- `.values` silently loses column labels and can silently upcast dtypes (e.g. an all-numeric-plus-one-text DataFrame becomes an `object` array) — prefer `.to_numpy()` when you specifically want a homogeneous array and know what dtype you're getting.
- `.describe()` ignores non-numeric columns unless you pass `include='all'` — easy to think a summary is complete when it silently dropped half your columns.
- A Series built from a dict takes its index from the dict keys, not `0..n-1` — mixing this up with the list-based default is a common source of "why is my index text" confusion.

## When it matters
Every pandas workflow starts here: loading or building a table, then immediately checking `.shape`, `.dtypes`, and `.info()` before doing anything else — skipping this step is how silent type/missing-data bugs sneak into later analysis.

## One-line recap example
```python
import pandas as pd
df = pd.DataFrame({"name": ["Alice", "Bob"], "salary": [95000, 62000]})
print(df.shape, df.dtypes["salary"], df["salary"].tolist())  # (2, 2) int64 [95000, 62000]
```
