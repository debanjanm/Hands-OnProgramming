# Input and Output — Notes

## What this covers
Writing and reading DataFrames to/from CSV, JSON, Excel, and a SQLite database — the common formats for getting data in and out of pandas.

## Key points
- `.to_csv(path, index=False)` — `index=False` skips writing the row index as its own column; without it, reloading gives a spurious `Unnamed: 0` column.
- `pd.read_csv()` key params: `dtype=` forces column types instead of letting pandas guess, `parse_dates=[...]` converts listed columns straight to `datetime64`, `usecols=[...]` loads only the needed columns (saves memory on wide files), `na_values=[...]` adds extra strings treated as missing.
- CSV has no type metadata — a date column reloads as plain string (`object` dtype) unless `parse_dates=` is passed explicitly.
- `.to_json(orient="records")` / `pd.read_json(orient="records")` — `orient="records"` produces a list of `{column: value}` dicts, the most portable layout for web APIs. JSON preserves numeric types better than CSV, but dates still round-trip as plain strings unless parsed again afterward.
- `.to_excel()` / `pd.read_excel()` need an extra engine library (`openpyxl` for `.xlsx`) that isn't bundled with pandas — check `import openpyxl` inside a `try`/`except ImportError` so a script degrades gracefully on a machine without it.
- `pd.read_sql(query, connection)` runs a SQL query against any DBI-style connection (e.g. `sqlite3.connect(":memory:")`) and returns the result directly as a DataFrame; `.to_sql(table, connection, index=False, if_exists="replace")` is the write-side equivalent, loading a DataFrame into a database table.

## Gotchas (the part worth revising twice)
- Forgetting `index=False` on `.to_csv()` is the most common CSV round-trip bug — the reloaded file gains an extra unnamed column holding the old row index.
- `parse_dates=` is not automatic — a CSV date column silently comes back as `object` (string) dtype without it, and downstream date operations (`.dt.year`, resampling, slicing) will fail or misbehave.
- Excel support is an optional dependency, not a pandas built-in — a script that assumes `openpyxl` is present will crash with `ImportError` on a fresh environment; always guard it.
- Temp files created for I/O demos should be cleaned up explicitly (`os.remove`) at the end of the script — they're scratch artifacts, not something to leave behind in the repo.

## When it matters
Reading and writing tabular data to disk or a database is the entry and exit point of almost every real pandas workflow — a script that loads a CSV, transforms it, and writes results back out (or into a database) is the most common shape of a data task.

## One-line recap example
```python
import pandas as pd
df.to_csv("orders.csv", index=False)
df2 = pd.read_csv("orders.csv", parse_dates=["order_date"])
```
