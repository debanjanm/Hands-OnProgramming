# Text and Datetime Deep Dive — Notes

## What this covers
The `.str` accessor beyond the basics (regex extraction, matching, splitting, replacing with functions, joining, padding, one-hot encoding, Unicode) and the datetime toolbox (`.dt`, `Period`, `Timedelta`, offsets, `date_range`, time zones and DST, `resample`, `asfreq`, intervals, messy-date parsing, epoch conversion, time buckets). Basics live in `03-Data-Cleaning` and `08-Time-Series`.

## Key points
- `str.extract(r"(?P<name>...)")` returns the first match as columns named by the groups; `str.extractall` returns every match with a `(row, match)` MultiIndex. Results are strings, so convert dtypes afterwards.
- `contains` searches anywhere, `match` anchors at the start, `fullmatch` needs the whole string. Pass `na=False` to get a clean boolean mask; use `regex=False` for literal text.
- `split(expand=True)` makes columns; `n=` limits splits; `rsplit` splits from the right; `partition`/`rpartition` always give exactly three pieces.
- In pandas 2.x `str.replace` has `regex=False` by default. A callable replacement receives a match object and needs `regex=True`.
- `str.cat` joins values (into one string, or element-wise with another Series); `str.join` joins the items of list cells.
- `zfill`, `pad`, `center` fix codes that lost leading zeros. `pd.get_dummies` one-hot encodes; `str.get_dummies("|")` handles multi-label cells.
- `normalize("NFC")` makes visually identical Unicode strings equal; `casefold()` is a stronger `lower()`.
- `.dt` gives `year`, `quarter`, `dayofweek` (Mon=0), `day_name()`, `is_month_end`, `floor/round`, `isocalendar()`.
- `Period` is a span (a month), `Timestamp` is a point. `to_period("M")` is handy for monthly grouping; `Q-MAR` makes fiscal quarters.
- Timedelta is fixed length; `DateOffset`, `MonthEnd`, `BDay`, `CustomBusinessDay` are calendar-aware.
- pandas 2.2 aliases: `h`, `min`, `s`, `D`, `ME`, `MS`, `QE`, `YE`, `B`, `W-FRI`.
- `tz_localize` attaches a zone; `tz_convert` changes the view of the same instant. Work in UTC, show local.
- `resample` has `closed`, `label`, `origin`, `offset`; `asfreq` only picks points (no aggregation).
- Parse dates with an explicit `format=`; use `errors="coerce"` and then inspect the NaT rows. `unit="s"/"ms"` converts epoch numbers.
- `pd.cut` on `dt.hour` builds time-of-day buckets; `right=False` gives `[a, b)` bins.

## Gotchas (the part worth revising twice)
- `str.contains` with missing values returns `NaN` in the mask, and boolean indexing then raises. Use `na=False`.
- `str.replace(r"\d+", ...)` silently does nothing useful on pandas 2.x unless `regex=True`.
- `extract` with no capture group raises `ValueError`; with several matches it keeps only the first one.
- `Timedelta.dt.seconds` is only the leftover seconds part, not the total. Use `total_seconds()`.
- `MonthEnd(1)` on a date that is already a month end jumps to the NEXT month end; `MonthEnd(0)` stays.
- `Jan 31 + DateOffset(months=1)` clips to Feb 29; `+ Timedelta(days=30)` does not. They answer different questions.
- Old aliases `H`, `M`, `Q`, `Y`, `T` warn in pandas 2.2. Use `h`, `ME`, `QE`, `YE`, `min`.
- Naive and aware timestamps cannot be compared or subtracted (`TypeError`).
- DST: a spring-forward local time does not exist (`NonExistentTimeError`) and a fall-back time happens twice (`AmbiguousTimeError`). Choose `nonexistent=` / `ambiguous=`. Adding 48 hours is not the same as adding 2 calendar days.
- Month-end resampling labels bins with the month END by default, other frequencies with the left edge.
- `03/04/2024` is 4 March without `dayfirst=True` or a format; ambiguous dates need an explicit format.
- `astype("int64")` on datetimes gives nanoseconds, not seconds. Reading milliseconds with `unit="s"` gives nonsense dates.
- `[1,2)` and `[2,3]` do not overlap; `[1,2]` and `[2,3]` do. `closed` matters.
- Same-looking Unicode text can have different code points and so be different group keys; normalize first.

## When it matters
Log parsing, ID and code cleanup, scheduling and booking conflict checks, month-end reporting, anything spanning time zones or daylight saving, and any import where dates arrive as messy text or epoch numbers.

## One-line recap example
```python
import pandas as pd
s = pd.Series(["id=7 on 2024-03-05", "id=9 on 2024-03-10"])
parts = s.str.extract(r"id=(?P<id>\d+) on (?P<day>[\d-]+)").assign(day=lambda t: pd.to_datetime(t["day"], format="%Y-%m-%d"))
```
