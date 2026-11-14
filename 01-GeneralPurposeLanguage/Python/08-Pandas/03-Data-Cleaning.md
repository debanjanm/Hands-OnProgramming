# Data Cleaning — Notes

## What this covers
Handling missing values, duplicate rows, messy/mixed-type columns, vectorized text cleanup with `.str`, and renaming columns — the standard first pass on any raw dataset.

## Key points
- `.isna()`/`.notna()` return a same-shape boolean mask; `.isna().sum()` is the standard per-column missing-value count.
- `.fillna(value)` fills with a scalar or a `{col: value}` dict; `.ffill()`/`.bfill()` (formerly `fillna(method='ffill'/'bfill')`) propagate the nearest valid value forward/backward — useful for ordered/time-series data.
- `.dropna()` defaults to dropping any row with any NaN (`axis=0, how='any'`); `axis=1` drops columns instead, `how='all'` only drops fully-empty rows/columns, `subset=[...]` restricts which columns are checked.
- `.duplicated()` flags rows that repeat an earlier row (`keep='first'` by default); `.drop_duplicates(subset=..., keep=...)` removes them, optionally checking only specific columns.
- `.astype(dtype)` converts type and returns a new object; a numeric-looking column becomes `dtype: object` the moment one value isn't cleanly numeric (e.g. `"N/A"`), because pandas can't mix types in a numeric dtype.
- `pd.to_numeric(series, errors='coerce')` is the fix for messy numeric columns — it converts what it can and turns unparseable values into `NaN` instead of raising.
- `.str` gives vectorized, NaN-aware string methods (`.str.upper()`, `.str.strip()`, `.str.contains()`, `.str.split()`) on a text column — no manual loop or `.apply()` needed.
- `.rename(columns={old: new})` renames specific columns without touching the rest.

## Gotchas (the part worth revising twice)
- A column reads as `object` dtype instead of numeric the instant one stray non-numeric value sneaks in — `.astype(float)` then raises `ValueError`; reach for `pd.to_numeric(..., errors='coerce')` instead.
- `.str.contains(pattern)` propagates `NaN` for missing values unless you pass `na=False`, which silently breaks a boolean mask used for filtering (`NaN` is truthy-ambiguous, not `False`).
- `.duplicated()`/`.drop_duplicates()` check for exact row/subset matches — near-duplicates (different casing, trailing whitespace) pass through untouched unless you clean the values first (e.g. with `.str.strip().str.lower()`).
- `.fillna(method='ffill')` still works but is deprecated in favor of calling `.ffill()`/`.bfill()` directly.

## When it matters
Real-world data always has gaps, repeats, and inconsistent types — skipping this pass means missing values silently break arithmetic, duplicate rows silently inflate aggregates, and mistyped columns silently fail comparisons.

## One-line recap example
```python
import pandas as pd
s = pd.Series(["19.99", "N/A", "5.50"])
pd.to_numeric(s, errors="coerce").fillna(0)  # [19.99, 0.0, 5.50]
```
