# Time Series — Notes

## What this covers
Turning date strings into real datetime data, building/using a `DatetimeIndex`, slicing by date, downsampling with `.resample()`, smoothing with `.rolling()`, computing lag/change with `.shift()`, and basic timezone handling.

## Key points
- `pd.to_datetime(series, errors="coerce")` parses strings into `datetime64` values; bad entries become `NaT` instead of raising (default `errors="raise"` stops on the first bad value).
- `pd.date_range(start=, periods=, freq=)` generates an evenly spaced `DatetimeIndex` (e.g. `freq="D"` for daily). Setting a `DatetimeIndex` (`df.set_index("date")`) is what unlocks date slicing, resampling, and time-aware rolling.
- Date slicing uses `.loc[]` for partial-string indexing: `df.loc["2024-01"]` matches the whole month, `df.loc["2024-01":"2024-03"]` matches a range with **both endpoints inclusive** (unlike normal Python slicing).
- `.resample(rule).agg(...)` buckets a `DatetimeIndex` into fixed periods (`"ME"` = month end, `"W"` = week) then aggregates — conceptually `groupby`, specialized for time: `resample` is `groupby` where the grouping key is always time.
- `.rolling(window=N).mean()` (or `.sum()`, `.std()`, etc.) computes over a sliding window of N consecutive rows — classic use is smoothing noisy daily data. The first `N-1` rows are `NaN` until enough history exists; `min_periods=1` avoids that warm-up gap.
- `.shift(n)` moves values down n rows (lag), `.shift(-n)` moves them up (lead) — the index stays put, only values move. Used for day-over-day change: `df["value"] - df["value"].shift(1)`.
- `tz_localize(tz)` **attaches** a timezone to naive timestamps (declares what zone they already represent, clock time unchanged); `tz_convert(tz)` **converts** an already tz-aware timestamp to a different zone (clock time shifts, same instant).

## Gotchas (the part worth revising twice)
- On a DataFrame, `df["2024-01"]` (no `.loc`) is read as a **column name lookup** and raises `KeyError` — partial-string date indexing on a DataFrame requires `.loc[]`.
- `.pivot()`-adjacent confusion: date slice endpoints are **inclusive** on both sides (`df.loc["2024-01":"2024-02"]` includes all of February), unlike `.iloc[]` or plain Python slicing where the stop is exclusive.
- `.rolling(window=N)` returns `NaN` for the first `N-1` rows by default — easy to mistake for a bug rather than expected warm-up behavior.
- Calling `tz_localize()` on a timestamp that's already tz-aware raises `TypeError` — you must `tz_convert()` (or strip the tz first) instead.

## When it matters
Almost every real dataset with a date column (sales, sensor readings, logs, stock prices) needs this toolkit: cleaning messy date strings, aggregating daily data to monthly reports, smoothing noisy trends, and computing period-over-period changes are everyday analysis tasks.

## One-line recap example
```python
import pandas as pd
df = df.set_index(pd.to_datetime(df["date"]))
monthly = df["revenue"].resample("ME").sum()   # daily -> monthly totals
```
