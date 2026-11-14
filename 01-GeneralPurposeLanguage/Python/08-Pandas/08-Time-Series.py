# 01. pd.to_datetime() - Parsing Strings to Datetime
# 02. pd.date_range() and Setting a DatetimeIndex
# 03. Date-Based Slicing
# 04. .resample() - Downsampling (resample vs groupby)
# 05. .rolling() - Window Calculations
# 06. .shift() - Lag/Lead Values
# 07. Timezone Basics - tz_localize / tz_convert

import pandas as pd
import numpy as np

# 01. pd.to_datetime() - Parsing Strings to Datetime
# ------------------------------------
# - Raw dates usually arrive as strings (from CSV, JSON, user input). Plain
#   string comparison/sorting doesn't understand calendar rules - you need a
#   real datetime dtype for date math, sorting, and resampling.
# - pd.to_datetime() parses strings (or a whole column of them) into
#   pandas Timestamp objects. It auto-detects most common formats.
# - errors='coerce' turns unparseable values into NaT (Not a Time) instead
#   of raising - use this on messy real-world data.

print("# 01. pd.to_datetime() - Parsing Strings to Datetime")
print("# ------------------------------------")

raw_dates = pd.Series(["2024-01-15", "2024-02-20", "not_a_date", "2024-03-10"])
print("raw_dates (strings):\n", raw_dates)

parsed_coerce = pd.to_datetime(raw_dates, errors="coerce")
print("\npd.to_datetime(errors='coerce') - bad values become NaT:\n", parsed_coerce)
print("dtype:", parsed_coerce.dtype)

try:
    pd.to_datetime(raw_dates, errors="raise")
except Exception as e:
    print("\nerrors='raise' (default) raises on 'not_a_date':", type(e).__name__, "-", str(e)[:80])

# 02. pd.date_range() and Setting a DatetimeIndex
# ------------------------------------
# - pd.date_range(start, end/periods, freq) generates an evenly-spaced
#   sequence of dates - handy for building a calendar or index from scratch.
# - Setting a DatetimeIndex (instead of a plain column) is what unlocks
#   date-based slicing, .resample(), and time-aware .rolling().

print("\n# 02. pd.date_range() and Setting a DatetimeIndex")
print("# ------------------------------------")

dates = pd.date_range(start="2024-01-01", periods=90, freq="D")
print("pd.date_range(start='2024-01-01', periods=90, freq='D')[:5] =\n", dates[:5])

rng = np.random.default_rng(42)
sales = pd.DataFrame({
    "date": dates,
    "units_sold": rng.integers(50, 200, size=90),
    "revenue": rng.uniform(500, 3000, size=90).round(2),
})
sales = sales.set_index("date")
print("\nsales with DatetimeIndex (head):\n", sales.head())
print("Index type:", type(sales.index).__name__)

# 03. Date-Based Slicing
# ------------------------------------
# - With a DatetimeIndex, string-based slices like df.loc['2024-01':'2024-02']
#   work as PARTIAL-STRING indexing - pandas expands '2024-01' to the whole
#   month automatically. Both endpoints are INCLUSIVE (unlike normal Python
#   slicing).
# - GOTCHA: on a DataFrame, plain df['2024-01'] (no .loc) is interpreted as a
#   COLUMN lookup and raises KeyError - partial-string indexing on a
#   DataFrame needs .loc[]. A bare slice like df['2024-01':'2024-02'] does
#   still work because Python routes a *slice* object to row-based lookup,
#   but a single label does not - so .loc[] is the safe habit either way.

print("\n# 03. Date-Based Slicing")
print("# ------------------------------------")

jan_slice = sales.loc["2024-01"]
print("sales.loc['2024-01'] (whole month of January) - rows:", len(jan_slice))

jan_to_feb = sales.loc["2024-01":"2024-02"]
print("sales.loc['2024-01':'2024-02'] - rows:", len(jan_to_feb),
      "(both endpoints inclusive, unlike df.iloc[a:b])")

try:
    sales["2024-01"]
except KeyError as e:
    print("\nGOTCHA - sales['2024-01'] (no .loc) raises KeyError:", e, "- treated as a column name")

single_day = sales.loc["2024-01-15"]
print("\nsales.loc['2024-01-15'] (single day):\n", single_day)

# 04. .resample() - Downsampling (resample vs groupby)
# ------------------------------------
# - .resample(rule) buckets a DatetimeIndex into fixed time periods (e.g.
#   'ME' = month end, 'W' = week) then you apply an aggregation, same as
#   groupby but the "groups" are automatically time buckets.
# - Mental model: resample IS groupby, specialized for time - `df.resample('ME')`
#   is roughly `df.groupby(pd.Grouper(freq='ME'))`. Use resample when the
#   grouping key is time; use groupby for any other categorical key.

print("\n# 04. .resample() - Downsampling (resample vs groupby)")
print("# ------------------------------------")

monthly_totals = sales.resample("ME").sum()
print("sales.resample('ME').sum() - daily -> monthly totals:\n", monthly_totals)

monthly_multi_agg = sales.resample("ME").agg({"units_sold": "sum", "revenue": "mean"})
print("\nDifferent agg per column via .agg({...}):\n", monthly_multi_agg)
print("# 'ME' = month end frequency (pandas >= 2.2; 'M' is deprecated for this purpose).")

# 05. .rolling() - Window Calculations
# ------------------------------------
# - .rolling(window=N) creates a sliding window of N consecutive rows; chain
#   an aggregation (.mean(), .sum(), .std()...) to compute it per window.
# - Classic use: smoothing noisy daily data with a rolling average - the
#   first (N-1) rows are NaN because there aren't yet N rows to average.

print("\n# 05. .rolling() - Window Calculations")
print("# ------------------------------------")

sales["revenue_7d_avg"] = sales["revenue"].rolling(window=7).mean()
print("7-day rolling average of revenue (smooths daily noise), head(10):\n",
      sales[["revenue", "revenue_7d_avg"]].head(10))
print("# First 6 rows are NaN - rolling(window=7) needs 7 real values before it can compute.")
print("#   Pass min_periods=1 to get a partial average instead of NaN during the warm-up.")

# 06. .shift() - Lag/Lead Values
# ------------------------------------
# - .shift(n) moves values DOWN by n rows (a "lag"), leaving NaN at the top;
#   .shift(-n) moves them UP (a "lead"). The index doesn't move - only the
#   values do, so row i now holds the value that used to be at row i-n.
# - Classic use: day-over-day change = today's value minus yesterday's,
#   which needs yesterday's value ALIGNED onto today's row.

print("\n# 06. .shift() - Lag/Lead Values")
print("# ------------------------------------")

sales["revenue_prev_day"] = sales["revenue"].shift(1)
sales["revenue_change"] = sales["revenue"] - sales["revenue_prev_day"]
print("Day-over-day revenue change, head():\n",
      sales[["revenue", "revenue_prev_day", "revenue_change"]].head())
print("# Row 0's revenue_prev_day is NaN - there's no prior day to shift in.")

# 07. Timezone Basics - tz_localize / tz_convert
# ------------------------------------
# - A "naive" datetime has no timezone attached - pandas doesn't know if
#   it's UTC, local time, or anything else.
# - tz_localize(tz) ATTACHES a timezone to naive timestamps (declares what
#   they already mean - doesn't shift the clock time).
# - tz_convert(tz) CONVERTS an already-tz-aware timestamp to a different
#   zone (does shift the clock time, since it's the same instant elsewhere).

print("\n# 07. Timezone Basics - tz_localize / tz_convert")
print("# ------------------------------------")

naive_ts = pd.Timestamp("2024-06-15 09:00:00")
print("naive_ts (no tz info):", naive_ts, "| tz:", naive_ts.tz)

localized_utc = naive_ts.tz_localize("UTC")
print("tz_localize('UTC') attaches UTC (same clock time, now tz-aware):", localized_utc)

converted_ny = localized_utc.tz_convert("America/New_York")
print("tz_convert('America/New_York') shifts the clock to the same instant elsewhere:", converted_ny)
print("# tz_localize: 'this naive timestamp IS this zone'. tz_convert: 'show me the same")
print("#   instant AS SEEN FROM a different zone'. Calling tz_localize twice raises TypeError.")

print("\n# End of Time Series")
