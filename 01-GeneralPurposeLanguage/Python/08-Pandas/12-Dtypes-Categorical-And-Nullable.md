# Dtypes, Categorical and Nullable — Notes

## What this covers
How pandas stores data: the `category` dtype (ordered, `.cat` accessor, memory saving, the groupby `observed` trap), the nullable dtypes (`Int64`, `Float64`, `boolean`, `string`) and `pd.NA` logic, `convert_dtypes`, `to_numeric`, downcasting, `memory_usage(deep=True)`, sparse data, optional pyarrow dtypes, NaN-related dtype pitfalls, and Copy-on-Write / `SettingWithCopy`. Basic `astype` and missing values are in 03/04; reading with `dtype=` is in 09; speed tips are in 10.

## Key points
- `category` stores unique values once plus small integer codes. Missing values have code `-1` and are never a category. Setting a value outside the categories raises `TypeError`.
- `pd.CategoricalDtype([...], ordered=True)` gives a real order: `<`, `>`, `min`, `max`, `sort_values` follow it. Values not in the list become NaN, which exposes typos.
- `.cat.add_categories`, `remove_categories`, `remove_unused_categories`, `rename_categories`, `reorder_categories`, `set_categories`, `as_ordered` manage the category list. Each returns a new Series.
- Category saves a lot of memory when there are few unique values (about 50x in the demo); with mostly unique values it is bigger than `object`.
- Always write `groupby(..., observed=True/False)`. `observed=False` returns a row for every category (even unused: sum 0, mean NaN); `observed=True` returns only the ones seen.
- `Int64`, `Float64`, `boolean`, `string` (capital letters for numbers) keep their type when data is missing and use `pd.NA`. Plain `int64` plus one NaN becomes `float64`.
- `pd.NA` means "unknown": `NA == NA` is NA, `bool(NA)` raises. Three-valued logic: `True | NA` is True, `False & NA` is False, `True & NA` and `False | NA` are NA.
- `df.convert_dtypes()` picks the best nullable dtype per column (optionally `dtype_backend="pyarrow"`).
- `pd.to_numeric(s, errors="coerce")` turns bad text into NaN; `downcast="integer"/"unsigned"/"float"` picks the smallest safe dtype; `dtype_backend="numpy_nullable"` returns `Int64`/`Float64`.
- `memory_usage(deep=True)` counts the real size of strings; the default counts only pointers.
- Sparse dtypes store only non-fill values: worth it for very empty data (one-hot columns).
- pyarrow dtypes (`"int64[pyarrow]"`, `"string[pyarrow]"`) exist only if pyarrow is installed; guard the import.
- Copy-on-Write (`pd.options.mode.copy_on_write = True`) makes every derived object act like a copy and is the only mode in pandas 3.

## Gotchas (the part worth revising twice)
- Forgetting `observed=` on a categorical groupby: warning in pandas 2.2, surprise empty groups, and big slow outputs when several categorical keys multiply.
- `astype("int8")` on out-of-range values silently wraps (300 becomes 44). Small int math also overflows. Check min/max or use `to_numeric(downcast=...)`.
- `astype(int)` on a column with NaN raises `IntCastingNaNError`; use `"Int64"`. `astype(str)` turns NaN into the text `"nan"`; use `"string"` to keep the missing value.
- A column of `object` can hide mixed types (`"5" + "5"` is `"55"`). Merges that add missing rows silently turn int columns into float.
- A `boolean` column containing NA cannot be used directly as a row mask; `fillna(False)` first.
- `df[mask]["col"] = value` modifies a temporary copy and the original stays unchanged (with a `SettingWithCopyWarning`). Use `df.loc[mask, "col"] = value`, or `.copy()` when you want an independent frame.
- `to_numeric(errors="ignore")` is deprecated; use `coerce` and handle NaN.

## When it matters
Large datasets (memory and speed), data with missing integers or booleans (IDs, flags, counts), survey-style ordered answers, and any pipeline where silent dtype changes would corrupt results. Fixing dtypes right after loading saves trouble later.

## One-line recap example
```python
import pandas as pd
s = pd.Series(["low", "high", "low"], dtype=pd.CategoricalDtype(["low", "mid", "high"], ordered=True))
s.groupby(s, observed=True).size()  # ordered category; observed= written explicitly
```
