# 01. Setup and the Plan
# 02. str.extract and str.extractall with Named Groups
# 03. str.contains, match, fullmatch with Regex and na=
# 04. str.split(expand), rsplit, partition
# 05. str.replace with Regex and Callables
# 06. str.cat and str.join
# 07. str.pad, ljust/rjust/center, zfill
# 08. get_dummies and str.get_dummies
# 09. Unicode: normalize and casefold
# 10. The dt Accessor
# 11. Period and PeriodIndex
# 12. Timedelta Arithmetic and to_timedelta
# 13. DateOffset, BusinessDay, MonthEnd
# 14. date_range and Frequency Aliases (pandas 2.2)
# 15. Time Zones and the DST Gotcha
# 16. resample: closed, label, origin
# 17. asfreq vs resample
# 18. Intervals and Overlap
# 19. Parsing Messy Dates: format, errors, dayfirst
# 20. Epoch Conversion
# 21. Bucketing by Time with cut
#
# Related: 03-Data-Cleaning (basic .str), 08-Time-Series (basics).
# This file goes deeper and does not repeat those basics.

import pandas as pd
import numpy as np

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)

# 01. Setup and the Plan
# ----------------------------
# - Part 1 (sections 02-09): the .str accessor in depth.
# - Part 2 (sections 10-21): dates, periods, timedeltas, time zones.
# - Everything is seeded or hand-written, so output is the same every run.
# - .str works only on object/string dtype. On numbers it raises AttributeError.

print("pandas", pd.__version__)
print("Part 1 = text, Part 2 = datetime")

# 02. str.extract and str.extractall with Named Groups
# ----------------------------
# - extract(pattern) pulls the FIRST match; each regex group becomes a column.
# - Named groups (?P<name>...) become the column names - self-documenting.
# - extractall returns EVERY match, with a MultiIndex (row, match number).
# - No match -> NaN for extract (not an error).
# - Pattern needs at least one capture group, or extract raises ValueError.

logs = pd.Series([
    "user=alice id=101 ip=10.0.0.1",
    "user=bob id=202 ip=10.0.0.22",
    "no data here",
    "user=carol id=303 ip=192.168.1.5",
])
parts = logs.str.extract(r"user=(?P<user>\w+) id=(?P<id>\d+) ip=(?P<ip>[\d.]+)")
print("extract with named groups:\n", parts, sep="")
parts["id"] = parts["id"].astype("Int64")  # extract gives strings; convert after
print("id dtype after astype:", parts["id"].dtype)

phones = pd.Series(["call 555-1234 or 555-9876", "none", "x 555-0000"])
print("\nextractall (all matches, MultiIndex):\n", phones.str.extractall(r"(?P<num>\d{3}-\d{4})"), sep="")
print("\nfirst level = original row, 'match' level = match number")
print("Gotcha demo: extract keeps only the first match ->")
print(phones.str.extract(r"(\d{3}-\d{4})")[0].tolist())
try:
    logs.str.extract(r"user=\w+")
except ValueError as e:
    print("No capture group ->", type(e).__name__, ":", e)

# 03. str.contains, match, fullmatch with Regex and na=
# ----------------------------
# - contains: pattern found ANYWHERE (regex=True by default).
# - match: pattern must match from the START (like re.match), not necessarily the end.
# - fullmatch: the WHOLE string must match.
# - na=False makes missing values count as "no match" so the mask is a clean bool.
#   Without it, the mask contains NaN and boolean indexing fails.
# - regex=False for plain text: faster and no need to escape special characters.
# - case=False / flags=re.IGNORECASE for case-insensitive search.

import re

s = pd.Series(["apple pie", "Apple", "pineapple", None, "a.b", "banana"])
print("series:", s.tolist())
print("contains 'apple' (default):", s.str.contains("apple").tolist())
print("contains 'apple', na=False:", s.str.contains("apple", na=False).tolist())
print("contains 'apple', case=False:", s.str.contains("apple", case=False, na=False).tolist())
print("match '^app' (start only):", s.str.match("app", na=False).tolist())
print("match 'apple' on 'pineapple' ->", s.str.match("apple", na=False).tolist())
print("fullmatch r'[Aa]pple':", s.str.fullmatch(r"[Aa]pple", na=False).tolist())
print("contains '.' regex=True (dot = any char):", s.str.contains(".", na=False).tolist())
print("contains '.' regex=False (literal dot):", s.str.contains(".", regex=False, na=False).tolist())
print("flags=re.I:", s.str.contains("APPLE", flags=re.IGNORECASE, na=False).tolist())
try:
    s[s.str.contains("apple")]
except ValueError as e:
    print("Mask with NaN in boolean indexing ->", type(e).__name__)

# 04. str.split(expand), rsplit, partition
# ----------------------------
# - split(sep) returns a LIST per row; expand=True makes separate columns.
# - n= limits the number of splits. rsplit splits from the RIGHT.
# - partition always gives exactly 3 pieces: (before, separator, after).
#   rpartition does the same from the right. Predictable shape = fewer surprises.
# - .str.get(i) or .str[i] picks the i-th element of the list after split.
# - split uses regex when the pattern is longer than 1 char (default regex=None
#   treats len>1 as regex); pass regex=False to be safe.

paths = pd.Series(["usr/local/bin/python", "home/user/file.txt", "single"])
print("split -> lists:", paths.str.split("/").tolist())
print("split n=1:", paths.str.split("/", n=1).tolist())
print("rsplit n=1:", paths.str.rsplit("/", n=1).tolist())
print("\nsplit(expand=True) pads short rows with None:\n", paths.str.split("/", expand=True), sep="")
print("\n.str.split('/').str[-1] (last piece):", paths.str.split("/").str[-1].tolist())
print("\nrpartition on '.':\n", pd.Series(["a.b.c", "nodot"]).str.rpartition("."), sep="")
print("\nregex split on commas OR semicolons:", pd.Series(["a,b;c"]).str.split(r"[,;]").tolist())
print("Gotcha: 'nodot' rpartition puts the whole string in the LAST column")

# 05. str.replace with Regex and Callables
# ----------------------------
# - In pandas 2.x str.replace defaults to regex=False. You MUST say regex=True
#   to use patterns (old pandas defaulted to True - old tutorials mislead).
# - repl can be a function: it receives a re.Match object and returns a string.
# - Backreferences \1, \2 work in the replacement string.
# - Callables need regex=True (a callable with regex=False raises ValueError).

t = pd.Series(["Price: $5", "cost $120 now", "$7 and $8"])
print("default regex=False treats pattern as literal text:", t.str.replace(r"\d+", "N").tolist())
print("regex=True:", t.str.replace(r"\d+", "N", regex=True).tolist())
print("callable doubles each number:",
      t.str.replace(r"\d+", lambda m: str(int(m.group()) * 2), regex=True).tolist())
print("backreference swap 'last, first' -> 'first last':",
      pd.Series(["Doe, Jane", "Roe, Rick"]).str.replace(r"(\w+), (\w+)", r"\2 \1", regex=True).tolist())
print("named group in callable:",
      pd.Series(["2024-03-05"]).str.replace(r"(?P<y>\d{4})-(?P<m>\d\d)-(?P<d>\d\d)",
                                              lambda m: f"{m['d']}/{m['m']}/{m['y']}", regex=True).tolist())
try:
    t.str.replace(r"\d+", lambda m: "N", regex=False)
except ValueError as e:
    print("callable + regex=False ->", type(e).__name__)

# 06. str.cat and str.join
# ----------------------------
# - str.cat(sep=...) concatenates all the values into ONE string (others=None),
#   or element-wise with another Series/list (others=...).
# - na_rep fills missing values; without it, NaN rows are skipped (single string)
#   or become NaN (element-wise).
# - str.join(sep) is DIFFERENT: it joins the elements of lists stored in each cell.
# - For plain column concatenation, `df["a"] + " " + df["b"]` also works
#   (but NaN propagates).

first = pd.Series(["Ann", "Bo", None])
last = pd.Series(["Lee", None, "Ray"])
print("cat all into one:", first.str.cat(sep="|"))
print("cat all with na_rep:", first.str.cat(sep="|", na_rep="?"))
print("element-wise with other:", first.str.cat(last, sep=" ").tolist())
print("element-wise with na_rep:", first.str.cat(last, sep=" ", na_rep="-").tolist())
print("operator +:", (first + " " + last).tolist())
lists = pd.Series([["a", "b"], ["c"], []])
print("join list cells:", lists.str.join("+").tolist())

# 07. str.pad, ljust/rjust/center, zfill
# ----------------------------
# - pad(width, side, fillchar) is the general tool; ljust/rjust/center are shortcuts.
# - zfill(width) pads with zeros on the left (keeps a leading sign correctly).
# - Great for fixing codes whose leading zeros were lost when read as numbers.
# - Never truncates: strings longer than width are returned unchanged.

codes = pd.Series([7, 42, 12345]).astype(str)
print("zfill(5):", codes.str.zfill(5).tolist())
print("pad right with '.':", codes.str.pad(6, side="right", fillchar=".").tolist())
print("center(7,'*'):", codes.str.center(7, "*").tolist())
print("zfill keeps sign:", pd.Series(["-5", "+3"]).str.zfill(4).tolist())
print("ZIP fix example:", pd.Series([2134, 501, 90210]).astype(str).str.zfill(5).tolist())
print("Gotcha: read_csv turns '00501' into 501 - use dtype=str on read, zfill is the repair")

# 08. get_dummies and str.get_dummies
# ----------------------------
# - pd.get_dummies(series_or_df) one-hot encodes a categorical column.
# - dtype=int (or bool) controls output; pandas 2.x returns bool by default.
# - drop_first=True drops one column to avoid the dummy-variable trap in models.
# - Series.str.get_dummies(sep) handles MULTI-LABEL cells like "a|b|c".
# - Missing values give all zeros (unless dummy_na=True adds a NaN column).

color = pd.Series(["red", "blue", "red", None])
print("get_dummies default dtype:", pd.get_dummies(color).dtypes.unique().tolist())
print("get_dummies dtype=int, dummy_na=True:\n", pd.get_dummies(color, dtype=int, dummy_na=True), sep="")
print("\ndrop_first:\n", pd.get_dummies(pd.Series(["a", "b", "c"]), drop_first=True, dtype=int), sep="")
tags = pd.Series(["py|sql", "py", "sql|bash|py", None])
print("\nstr.get_dummies(sep='|') multi-label:\n", tags.str.get_dummies("|"), sep="")
df = pd.DataFrame({"size": ["S", "M"], "price": [10, 20]})
print("\nget_dummies on a DataFrame only encodes object columns, with prefix:\n",
      pd.get_dummies(df, dtype=int), sep="")

# 09. Unicode: normalize and casefold
# ----------------------------
# - The same visible text can be different code points ("e" + accent vs one "é").
#   Equality, groupby and merge then treat them as different keys!
# - str.normalize('NFC') (or 'NFKC') makes them consistent.
# - casefold() is a stronger lower(): the German "ß" -> "ss".
# - To strip accents: normalize('NFKD') then drop non-ASCII combining marks.

a = "café"        # one code point
b = "café"       # e + combining accent
u = pd.Series([a, b])
print("look identical:", u.tolist(), "| equal?", a == b, "| lens:", u.str.len().tolist())
print("unique values before:", u.nunique(), "-> after NFC:", u.str.normalize("NFC").nunique())
print("lower vs casefold on 'Straße':", pd.Series(["Straße"]).str.lower().tolist(),
      pd.Series(["Straße"]).str.casefold().tolist())
stripped = u.str.normalize("NFKD").str.encode("ascii", errors="ignore").str.decode("ascii")
print("accents stripped:", stripped.tolist())
print("NFKC folds compat chars (full-width 'ＡＢＣ'):", pd.Series(["ＡＢＣ"]).str.normalize("NFKC").tolist())

# 10. The dt Accessor
# ----------------------------
# - Series.dt works on datetime64 columns (convert with pd.to_datetime first).
# - Properties: year, month, day, hour, quarter, dayofweek (Mon=0), dayofyear.
# - Methods: day_name(), month_name(), is_month_end, is_quarter_start, floor/ceil/round.
# - normalize() sets time to midnight; dt.date gives python dates (object dtype - slow).
# - dt.isocalendar() returns ISO year/week/day as a DataFrame.

d = pd.Series(pd.to_datetime(["2024-01-31 15:45", "2024-02-29 08:10", "2024-03-01 23:59", "2024-12-30 00:00"]))
info = pd.DataFrame({
    "ts": d, "year": d.dt.year, "quarter": d.dt.quarter, "dow": d.dt.dayofweek,
    "day_name": d.dt.day_name(), "month": d.dt.month_name(),
    "month_end": d.dt.is_month_end, "doy": d.dt.dayofyear,
})
print(info)
print("\nfloor('h'):", d.dt.floor("h").dt.strftime("%H:%M").tolist())
print("round('D'):", d.dt.round("D").dt.strftime("%m-%d").tolist())
print("normalize:", d.dt.normalize().dt.strftime("%m-%d %H:%M").tolist())
print("\nisocalendar (2024-12-30 belongs to ISO week 1 of 2025!):\n", d.dt.isocalendar(), sep="")
print("strftime:", d.dt.strftime("%d %b %Y").tolist())

# 11. Period and PeriodIndex
# ----------------------------
# - A Timestamp is a POINT in time; a Period is a SPAN (a whole month, quarter...).
# - Period('2024-03', 'M') covers all of March. Arithmetic shifts by whole units.
# - to_period('M') on dates turns them into months - handy for monthly grouping.
# - .start_time / .end_time give the span's boundaries (end_time = last nanosecond).
# - Fiscal years: freq 'Q-MAR' makes quarters that end in March.

p = pd.Period("2024-03", "M")
print("Period:", p, "| +2:", p + 2, "| start:", p.start_time, "| end:", p.end_time)
print("days in month:", p.days_in_month)
pi = pd.period_range("2024-01", periods=4, freq="M")
print("period_range:", pi.tolist())
dates = pd.Series(pd.to_datetime(["2024-01-15", "2024-01-20", "2024-02-03"]))
print("to_period('M'):", dates.dt.to_period("M").astype(str).tolist())
print("count per month:\n", dates.dt.to_period("M").value_counts().sort_index(), sep="")
print("Quarter ending March (fiscal):", pd.Period("2024-01-15", "Q-MAR"), "| start:", pd.Period("2024-01-15", "Q-MAR").start_time.date())
print("Period difference (in months):", (pd.Period("2024-06", "M") - pd.Period("2023-11", "M")).n)
print("Period -> back to_timestamp():", pd.Period("2024-03", "M").to_timestamp())

# 12. Timedelta Arithmetic and to_timedelta
# ----------------------------
# - datetime - datetime = Timedelta. datetime +/- Timedelta = datetime.
# - Timedelta has .days, .seconds (the leftover seconds part, NOT total!),
#   and .total_seconds() for the full amount. Use total_seconds().
# - Series.dt.total_seconds() / dt.days work on whole columns.
# - pd.to_timedelta parses strings like "1d 2h" or numbers with a unit.
# - Divide a Timedelta by another Timedelta to get a plain float ratio.

start = pd.Series(pd.to_datetime(["2024-01-01 08:00", "2024-01-01 09:30"]))
end = pd.Series(pd.to_datetime(["2024-01-03 10:15", "2024-01-01 17:45"]))
dur = end - start
print("durations:", dur.astype(str).tolist())
print("dt.days:", dur.dt.days.tolist(), "| dt.seconds (leftover only!):", dur.dt.seconds.tolist())
print("total_seconds:", dur.dt.total_seconds().tolist())
print("in hours:", (dur / pd.Timedelta(hours=1)).tolist())
print("to_timedelta('90min'):", pd.to_timedelta("90min"), "| numbers+unit:", pd.to_timedelta([1.5, 2], unit="h").tolist())
print("to_timedelta('1 days 02:03:04'):", pd.to_timedelta("1 days 02:03:04"))
print("timestamp + Timedelta:", pd.Timestamp("2024-02-28 12:00") + pd.Timedelta(days=2, hours=3))
print("Timedelta ratio:", pd.Timedelta(days=1) / pd.Timedelta(hours=6))
print("Gotcha: Timedelta has no 'month' unit (months vary). Use DateOffset/Period for that.")

# 13. DateOffset, BusinessDay, MonthEnd
# ----------------------------
# - Offsets are calendar-aware steps (unlike Timedelta which is fixed length).
# - pd.DateOffset(months=1) respects month lengths: Jan 31 + 1 month = Feb 29 (clipped).
# - MonthEnd / MonthBegin roll to the next boundary. If already ON it, MonthEnd(1) moves
#   to the NEXT month end; MonthEnd(0) stays put (the classic trick).
# - BusinessDay (BDay) skips Saturday/Sunday. CustomBusinessDay takes holidays.
# - offset.rollforward / rollback snap a date to the nearest valid one.

from pandas.tseries.offsets import BDay, MonthEnd, MonthBegin, CustomBusinessDay

jan31 = pd.Timestamp("2024-01-31")
print("Jan 31 + DateOffset(months=1):", (jan31 + pd.DateOffset(months=1)).date())
print("Jan 31 + 30 days (Timedelta):", (jan31 + pd.Timedelta(days=30)).date())
print("MonthEnd(1) from Jan 15:", (pd.Timestamp("2024-01-15") + MonthEnd(1)).date())
print("MonthEnd(1) from Jan 31 (already end) -> NEXT:", (jan31 + MonthEnd(1)).date())
print("MonthEnd(0) from Jan 31 -> stays:", (jan31 + MonthEnd(0)).date())
print("MonthBegin from Jan 15:", (pd.Timestamp("2024-01-15") + MonthBegin(1)).date())
fri = pd.Timestamp("2024-03-01")  # Friday
print("Friday + BDay(1):", (fri + BDay(1)).date(), "(Monday) | +BDay(5):", (fri + BDay(5)).date())
cbd = CustomBusinessDay(holidays=["2024-03-04"])
print("with Monday holiday, Fri + 1 bday:", (fri + cbd).date())
sat = pd.Timestamp("2024-03-02")
print("Saturday rollforward:", BDay().rollforward(sat).date(), "| rollback:", BDay().rollback(sat).date())
print("Feb 29 + 1 year clips to Feb 28:", (pd.Timestamp("2024-02-29") + pd.DateOffset(years=1)).date())

# 14. date_range and Frequency Aliases (pandas 2.2)
# ----------------------------
# - date_range(start, end | periods, freq). Give exactly 3 of start/end/periods/freq.
# - pandas 2.2 renamed aliases. Use: 'h' (hour), 'min', 's', 'D', 'W', 'ME' (month end),
#   'MS' (month start), 'QE' (quarter end), 'YE' (year end), 'B' (business day).
# - Old 'H', 'M', 'Q', 'Y', 'T' are deprecated: they warn (FutureWarning) in 2.2.
# - Multipliers work: '2h', '15min', '2W-MON'. Anchored weekly: 'W-FRI'.
# - inclusive='left'/'right'/'both'/'neither' controls endpoints.

print("daily:", pd.date_range("2024-01-01", periods=3, freq="D").strftime("%m-%d").tolist())
print("'h' every 6 hours:", pd.date_range("2024-01-01", periods=3, freq="6h").strftime("%d %H:%M").tolist())
print("'ME' month ends:", pd.date_range("2024-01-01", "2024-04-30", freq="ME").strftime("%m-%d").tolist())
print("'MS' month starts:", pd.date_range("2024-01-01", "2024-04-30", freq="MS").strftime("%m-%d").tolist())
print("'QE' quarter ends:", pd.date_range("2024-01-01", "2024-12-31", freq="QE").strftime("%m-%d").tolist())
print("'YE' year ends:", pd.date_range("2022-01-01", "2024-12-31", freq="YE").strftime("%Y-%m-%d").tolist())
print("'B' business days:", pd.date_range("2024-03-01", periods=4, freq="B").strftime("%a %d").tolist())
print("'W-FRI' Fridays:", pd.date_range("2024-03-01", periods=3, freq="W-FRI").strftime("%m-%d").tolist())
print("'15min':", pd.date_range("2024-01-01", periods=3, freq="15min").strftime("%H:%M").tolist())
print("inclusive='left':", pd.date_range("2024-01-01", "2024-01-04", freq="D", inclusive="left").strftime("%d").tolist())
print("linspace style (no freq): periods=3 between two dates:",
      pd.date_range("2024-01-01", "2024-01-03", periods=3).strftime("%d").tolist())
print("freq string of a range:", pd.date_range("2024-01-01", periods=2, freq="ME").freqstr)

# 15. Time Zones and the DST Gotcha
# ----------------------------
# - Naive timestamps have no zone. tz_localize ATTACHES a zone (the clock reading is
#   kept). tz_convert CHANGES zone (same instant, new clock reading).
# - Store/compute in UTC; convert to local time only for display.
# - Can't subtract/compare naive with aware (TypeError).
# - DST gotcha: in spring a local hour does not exist (nonexistent), in autumn one
#   hour happens twice (ambiguous). tz_localize raises unless you choose
#   ambiguous= / nonexistent=.
# - A 'D' step across DST in a tz-aware range keeps the clock time; adding 24h does not.

naive = pd.Series(pd.to_datetime(["2024-06-01 12:00", "2024-06-01 18:30"]))
ny = naive.dt.tz_localize("America/New_York")
print("localized:", ny.astype(str).tolist())
print("convert to UTC:", ny.dt.tz_convert("UTC").astype(str).tolist())
print("convert to Asia/Kolkata:", ny.dt.tz_convert("Asia/Kolkata").astype(str).tolist())
try:
    ny - naive
except TypeError as e:
    print("aware - naive ->", type(e).__name__)

spring = pd.Series(pd.to_datetime(["2024-03-10 02:30"]))   # skipped hour in New York
try:
    spring.dt.tz_localize("America/New_York")
except Exception as e:
    print("nonexistent time ->", type(e).__name__)
print("nonexistent='shift_forward':", spring.dt.tz_localize("America/New_York", nonexistent="shift_forward").astype(str).tolist())
print("nonexistent='NaT':", spring.dt.tz_localize("America/New_York", nonexistent="NaT").astype(str).tolist())
fall = pd.Series(pd.to_datetime(["2024-11-03 01:30"]))     # happens twice
try:
    fall.dt.tz_localize("America/New_York")
except Exception as e:
    print("ambiguous time ->", type(e).__name__)
print("ambiguous=True (DST):", fall.dt.tz_localize("America/New_York", ambiguous=[True]).astype(str).tolist())
print("ambiguous=False (standard):", fall.dt.tz_localize("America/New_York", ambiguous=[False]).astype(str).tolist())

day_range = pd.date_range("2024-03-09 12:00", periods=3, freq="D", tz="America/New_York")
print("freq='D' keeps 12:00 wall clock:", day_range.strftime("%m-%d %H:%M %z").tolist())
plus24 = pd.Timestamp("2024-03-09 12:00", tz="America/New_York") + pd.Timedelta(hours=48)
print("+48 hours lands on 13:00 wall clock:", plus24.strftime("%m-%d %H:%M %z"))

# 16. resample: closed, label, origin
# ----------------------------
# - resample needs a DatetimeIndex (or on='col'). Then call an aggregation.
# - closed='left'/'right' decides which side of each bin includes the edge.
# - label='left'/'right' decides which edge names the bin.
#   Defaults: left/left for most freqs, but right/right for 'ME', 'QE', 'YE', 'W'.
# - origin='start' / 'start_day' / 'epoch' / a Timestamp anchors where bins start.
#   Matters when freq doesn't divide a day evenly (e.g. '7min' or '90min').
# - offset= shifts bin edges by a Timedelta.

idx = pd.date_range("2024-01-01 00:00", periods=8, freq="15min")
ts = pd.Series(np.arange(1, 9), index=idx)
print("series 1..8 every 15min starting 00:00")
print("30min sum, closed=left label=left:\n", ts.resample("30min").sum(), sep="")
print("\nclosed=right label=right (edge belongs to previous bin):\n",
      ts.resample("30min", closed="right", label="right").sum(), sep="")
odd = pd.Series(1, index=pd.date_range("2024-01-01 00:10", periods=6, freq="10min"))
print("\n25min bins, origin='start_day' (midnight anchored):\n", odd.resample("25min").sum(), sep="")
print("\n25min bins, origin='start' (first timestamp anchored):\n", odd.resample("25min", origin="start").sum(), sep="")
print("\n25min bins, offset=5min:\n", odd.resample("25min", offset="5min").sum(), sep="")
m = pd.Series(1, index=pd.date_range("2024-01-15", periods=60, freq="D"))
print("\nmonthly 'ME' label is month END:\n", m.resample("ME").sum(), sep="")
print("\nresample().agg(['sum','mean','max']) is supported:\n", ts.resample("1h").agg(["sum", "mean", "max"]), sep="")

# 17. asfreq vs resample
# ----------------------------
# - resample = group into bins and AGGREGATE (many rows -> one).
# - asfreq = just PICK the values at the new frequency points (no aggregation).
# - asfreq with a finer freq creates NaN rows; fill with method='ffill' or fill_value.
# - Upsampling with resample needs an aggregator too: .ffill(), .interpolate(), .asfreq().
# - Use asfreq to expose gaps in a series that should be regular.

daily = pd.Series([10.0, 20.0, 40.0], index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-05"]))
print("irregular daily series:\n", daily, sep="")
print("\nasfreq('D') shows the missing days as NaN:\n", daily.asfreq("D"), sep="")
print("\nasfreq('D', method='ffill'):\n", daily.asfreq("D", method="ffill"), sep="")
print("\nasfreq('D', fill_value=0):", daily.asfreq("D", fill_value=0).tolist())
print("\nresample('D').interpolate():", daily.resample("D").interpolate().round(1).tolist())
hourly = pd.Series(range(6), index=pd.date_range("2024-01-01", periods=6, freq="h"))
print("asfreq('3h') just picks rows:", hourly.asfreq("3h").tolist(), "| resample('3h').sum():", hourly.resample("3h").sum().tolist())

# 18. Intervals and Overlap
# ----------------------------
# - pd.Interval(left, right, closed=...) is a range of values; works with numbers
#   and Timestamps. IntervalIndex holds many.
# - 'in' tests membership; .overlaps(other) tests two intervals.
# - closed matters: [1,2] and [2,3] overlap but [1,2) and [2,3] do NOT.
# - IntervalIndex.contains / get_indexer find which interval a value falls in.
# - Classic use: find booking conflicts or map events to shifts.

a = pd.Interval(pd.Timestamp("2024-01-01 09:00"), pd.Timestamp("2024-01-01 10:00"))
b = pd.Interval(pd.Timestamp("2024-01-01 09:30"), pd.Timestamp("2024-01-01 11:00"))
c = pd.Interval(pd.Timestamp("2024-01-01 10:00"), pd.Timestamp("2024-01-01 11:00"))
print("a overlaps b:", a.overlaps(b), "| a overlaps c (touch at 10:00, both closed right/left):", a.overlaps(c))
print("[1,2) overlaps [2,3]?", pd.Interval(1, 2, closed="left").overlaps(pd.Interval(2, 3, closed="both")))
print("[1,2] overlaps [2,3]?", pd.Interval(1, 2, closed="both").overlaps(pd.Interval(2, 3, closed="both")))
print("5 in Interval(0, 10):", 5 in pd.Interval(0, 10), "| length:", pd.Interval(0, 10).length)
bookings = pd.IntervalIndex.from_arrays(
    pd.to_datetime(["2024-01-01 09:00", "2024-01-01 09:30", "2024-01-01 13:00"]),
    pd.to_datetime(["2024-01-01 10:00", "2024-01-01 10:30", "2024-01-01 14:00"]),
    closed="left")
print("\nbookings:", [f"{i.left:%H:%M}-{i.right:%H:%M}" for i in bookings])
conflicts = [(i, j) for i in range(len(bookings)) for j in range(i + 1, len(bookings)) if bookings[i].overlaps(bookings[j])]
print("conflicting pairs (by position):", conflicts)
print("which booking holds 09:45?", bookings.contains(pd.Timestamp("2024-01-01 09:45")).tolist())
print("is_non_overlapping:", bookings.is_non_overlapping_monotonic)

# 19. Parsing Messy Dates: format, errors, dayfirst
# ----------------------------
# - Always pass format= when you know it: faster, strict, and unambiguous.
# - Without format, pandas 2.x guesses from the FIRST element and applies it to all
#   (and warns if it cannot infer consistently). Mixed formats -> use format='mixed'
#   or format='ISO8601'.
# - dayfirst=True reads 03/04/2024 as 3 April; default reads it as March 4.
# - errors='raise' (default) / 'coerce' (bad -> NaT) / 'ignore' (deprecated style).
# - After coerce, check isna() to find and log the bad rows - never ignore them.
# - '%Y%m%d' style compact strings need format too (or the number is read as epoch ns).

raw = pd.Series(["2024-03-05", "05/03/2024", "March 5, 2024", "not a date", None])
print("format='ISO8601', errors='coerce':", pd.to_datetime(raw, format="ISO8601", errors="coerce").astype(str).tolist())
print("format='mixed', errors='coerce':", pd.to_datetime(raw, format="mixed", errors="coerce").astype(str).tolist())
amb = pd.Series(["03/04/2024", "25/12/2024"])
print("\nmonth-first: ->", pd.to_datetime(amb, format="%m/%d/%Y", errors="coerce").astype(str).tolist())
print("explicit day-first format ->", pd.to_datetime(amb, format="%d/%m/%Y").astype(str).tolist())
print("format='mixed', dayfirst=True ->", pd.to_datetime(amb, format="mixed", dayfirst=True).astype(str).tolist())
bad = pd.to_datetime(raw, format="mixed", errors="coerce")
print("rows that failed to parse:", raw[bad.isna() & raw.notna()].tolist(), "| genuinely missing:", int(raw.isna().sum()))
print("compact %Y%m%d:", pd.to_datetime(pd.Series(["20240305", "20241231"]), format="%Y%m%d").dt.date.tolist())
print("Out-of-bounds year coerces to NaT:", pd.to_datetime(pd.Series(["3000-01-01"]), errors="coerce").astype(str).tolist())
print("Date parts from columns:", pd.to_datetime(pd.DataFrame({"year": [2024], "month": [3], "day": [5]})).astype(str).tolist())
print("Two-digit year with %y:", pd.to_datetime(pd.Series(["05-03-24"]), format="%d-%m-%y").astype(str).tolist())

# 20. Epoch Conversion
# ----------------------------
# - Unix time = seconds since 1970-01-01 UTC. Many APIs also use milliseconds.
# - pd.to_datetime(x, unit='s' | 'ms' | 'us' | 'ns') converts numbers to timestamps.
# - Wrong unit gives a date in 1970 (too big a unit) or an error/huge year - sanity check.
# - Back to epoch: .astype('int64') gives NANOSECONDS in pandas (not seconds!);
#   so divide by 10**9, or use (ts - epoch) // pd.Timedelta('1s').
# - Timestamps from epoch are UTC; use tz_localize('UTC').tz_convert(...) to display locally.

secs = pd.Series([0, 1_700_000_000, 1_709_600_000])
print("unit='s':", pd.to_datetime(secs, unit="s").astype(str).tolist())
ms = pd.Series([1_700_000_000_000])
print("ms read as 's' by mistake -> ", pd.to_datetime(ms, unit="s", errors="coerce").astype(str).tolist())
print("ms read correctly:", pd.to_datetime(ms, unit="ms").astype(str).tolist())
t0 = pd.to_datetime(secs, unit="s")
print("\nback to seconds via // Timedelta:", ((t0 - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")).tolist())
print("astype('int64') gives nanoseconds; // 10**9 gives seconds:", t0.astype("int64").iloc[1] // 10**9)
print("single Timestamp.timestamp():", pd.Timestamp("2024-03-05", tz="UTC").timestamp())
print("epoch -> local time:", pd.to_datetime(secs, unit="s", utc=True).dt.tz_convert("Asia/Kolkata").astype(str).tolist())

# 21. Bucketing by Time with cut
# ----------------------------
# - pd.cut on datetimes needs bins that are Timestamps (use date_range for edges).
# - For time-of-day buckets, cut the HOUR number (dt.hour) with integer bins and labels.
# - right=False makes bins [a, b) - usually what you want for hours.
# - Watch edges: a value on the leftmost edge is NaN unless include_lowest=True (or right=False).
# - groupby(dt.floor('h')) or Grouper(freq=...) is the alternative for regular buckets.

rng = np.random.default_rng(7)
events = pd.DataFrame({"ts": pd.Timestamp("2024-03-05") + pd.to_timedelta(rng.integers(0, 24 * 60, 12), unit="min")}).sort_values("ts").reset_index(drop=True)
events["hour"] = events["ts"].dt.hour
events["part"] = pd.cut(events["hour"], bins=[0, 6, 12, 18, 24], right=False,
                        labels=["night", "morning", "afternoon", "evening"])
print(events)
print("\ncounts per part of day (observed categories, in order):\n", events["part"].value_counts(sort=False), sep="")
edges = pd.date_range("2024-03-05", periods=5, freq="6h")
events["bucket"] = pd.cut(events["ts"], bins=edges, right=False)
print("\nTimestamp-edge bins (first 3 rows):\n", events[["ts", "bucket"]].head(3), sep="")
print("\ngroupby floor('3h') counts:\n", events.groupby(events["ts"].dt.floor("3h")).size(), sep="")
print("Weekend flag via dayofweek >= 5:", (pd.Series(pd.date_range("2024-03-01", periods=7)).dt.dayofweek >= 5).tolist())
print("Done.")
