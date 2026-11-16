# 01. transform - Group Results Broadcast Back
# 02. filter - Keep or Drop Whole Groups
# 03. apply - The Flexible (and Slow) Option
# 04. Named Aggregation and Several Functions at Once
# 05. Custom agg With Lambdas and Their Cost
# 06. rank Within Groups
# 07. cumcount and ngroup
# 08. nth, head, tail Per Group
# 09. rolling - Windows, min_periods, center
# 10. rolling With closed= and Time-Based Windows
# 11. rolling apply
# 12. expanding and ewm
# 13. Cumulative Ops, diff, pct_change
# 14. pipe, assign and Method Chaining
# 15. crosstab
# 16. merge_asof
# 17. merge indicator and validate
# 18. explode
# 19. combine_first and clip
# 20. nlargest, nsmallest, describe Tweaks and Sampling
#
# See also: 05-GroupBy-And-Aggregation (basics), 06-Merging-And-Joining (merge basics),
# 08-Time-Series (resample), 11-MultiIndex-And-Advanced-Indexing (query/eval/where).

import numpy as np
import pandas as pd

rng = np.random.default_rng(123)

sales = pd.DataFrame({
    "region": ["East", "East", "West", "West", "East", "West", "East", "West", "North", "North"],
    "rep": ["Alice", "Alice", "Bob", "Carla", "Dev", "Bob", "Alice", "Carla", "Esha", "Esha"],
    "units": [10, 5, 8, 12, 20, 15, 7, 9, 3, 4],
    "revenue": [99.9, 122.5, 79.9, 294.0, 199.8, 149.9, 171.5, 220.5, 45.0, 60.0],
})
print("sales:\n", sales, sep="")

# 01. transform - Group Results Broadcast Back
# -------------------------------------------------
# - transform returns a result with the SAME index as the input, so it can
#   be assigned straight back as a column (z-scores, shares, group means).
# - It accepts a name ("mean", "rank", "cumsum"), a function, or a lambda.
# - The function must return a scalar (broadcast) or same-length result.
# - Typical uses: share of group total, fill NaN with group mean,
#   standardise within group.

g = sales.groupby("region")["revenue"]
out = sales[["region", "revenue"]].copy()
out["group_mean"] = g.transform("mean").round(2)
out["share_%"] = (sales["revenue"] / g.transform("sum") * 100).round(1)
out["zscore"] = g.transform(lambda s: (s - s.mean()) / s.std(ddof=0)).round(2)
print(out)

gaps = pd.DataFrame({"k": ["a", "a", "b", "b"], "v": [1.0, np.nan, 10.0, np.nan]})
print("\nFill NaN with group mean:", gaps.groupby("k")["v"].transform(lambda s: s.fillna(s.mean())).tolist())

# 02. filter - Keep or Drop Whole Groups
# --------------------------------------------
# - groupby.filter(func) keeps ALL rows of groups where func(group) is True
#   and drops the rest. func must return a single True/False per group.
# - Result keeps original rows and index (no collapsing).
# - Different from boolean masks on rows: the test is about the group.

big = sales.groupby("region").filter(lambda d: d["revenue"].sum() > 200)
print("Regions with total revenue > 200 (North dropped):\n", big["region"].value_counts().to_dict(), sep="")
print("Groups with at least 3 rows:", sorted(sales.groupby("region").filter(lambda d: len(d) >= 3)["region"].unique()))

# 03. apply - The Flexible (and Slow) Option
# ------------------------------------------------
# - apply gives your function each group as a DataFrame; it can return a
#   scalar, a Series or a DataFrame, and pandas stitches the output.
# - It is the slowest route: a Python call per group and extra work to
#   guess the output shape. Prefer agg/transform when they can do it.
# - pandas 2.2: apply on a DataFrame GroupBy passes the grouping columns too,
#   which is deprecated. Select the columns you need after groupby (or use
#   include_groups=False) to keep it future-proof.
# - group_keys=False stops the group labels being added to the result index.

top1 = sales.groupby("region", group_keys=False)[["rep", "revenue"]].apply(lambda d: d.nlargest(1, "revenue"))
print("Best row per region (apply returning a DataFrame):\n", top1, sep="")
spread = sales.groupby("region")["revenue"].apply(lambda s: s.max() - s.min())
print("\nSeries apply returning a scalar per group:\n", spread.round(2), sep="")
nokeys = sales.groupby("region").apply(lambda d: d["units"].sum(), include_groups=False)
print("\ninclude_groups=False:", nokeys.to_dict())

# 04. Named Aggregation and Several Functions at Once
# --------------------------------------------------------
# - agg(new_name=("column", "func")) gives flat, readable output columns.
# - func can be a string, a callable, or pd.NamedAgg.
# - Passing a list agg(["sum", "mean"]) makes two-level columns; use
#   named aggregation to avoid MultiIndex columns.
# - Several named aggregations on the same column are allowed.

summary = sales.groupby("region").agg(
    n=("rep", "size"),
    reps=("rep", "nunique"),
    total_rev=("revenue", "sum"),
    avg_units=("units", "mean"),
    best=("revenue", "max"),
    best_again=pd.NamedAgg(column="revenue", aggfunc="max"),
).round(2)
print(summary)
print("\nList form on several columns gives two-level (MultiIndex) columns:", sales.groupby("region")[["units", "revenue"]].agg(["sum"]).columns.tolist())

# 05. Custom agg With Lambdas and Their Cost
# ------------------------------------------------
# - Built-in names ("sum", "mean", "max") run in fast compiled code.
# - A lambda/custom function runs once per group in Python: with many
#   groups this is far slower. Count the calls to see it.
# - Lambdas also give ugly column names ("<lambda>"); use named aggregation.
# - Several lambdas in one list agg get auto names like <lambda_0>, <lambda_1>:
#   hard to read and easy to mix up.
# - Vectorised alternatives: compute with built-ins first, then combine
#   (e.g. max - min via two named aggs and a column subtraction).

calls = {"n": 0}

def counted_range(s):
    calls["n"] += 1
    return s.max() - s.min()

many = pd.DataFrame({"k": np.repeat(np.arange(500), 4), "v": rng.normal(size=2000)})
r1 = many.groupby("k")["v"].agg(counted_range)
print("Python calls made by the custom function:", calls["n"], "(one per group, 500 groups)")
fast = many.groupby("k")["v"].agg(lo="min", hi="max")
r2 = fast["hi"] - fast["lo"]
print("Same answer with built-ins + subtraction:", np.allclose(r1.to_numpy(), r2.to_numpy()))
two = sales.groupby("region")["revenue"].agg([lambda s: s.min(), lambda s: s.max()])
print("Two unnamed lambdas get auto names:", two.columns.tolist())
print("One lambda column name:", sales.groupby("region")["revenue"].agg([lambda s: s.max()]).columns.tolist())

# 06. rank Within Groups
# ----------------------------
# - groupby(...).rank() ranks inside each group (starts again at 1).
# - method="average" (default), "min", "max", "first", "dense".
# - ascending=False ranks the biggest as 1. pct=True gives 0-1 position.
# - Use rank to pick "top N per group": rank <= N.

r = sales[["region", "revenue"]].copy()
r["rank_desc"] = sales.groupby("region")["revenue"].rank(ascending=False, method="first").astype(int)
r["pct"] = sales.groupby("region")["revenue"].rank(pct=True).round(2)
print(r.sort_values(["region", "rank_desc"]))
ties = pd.Series([5, 5, 7, 9])
print("\nTies, method average/min/dense/first:",
      ties.rank().tolist(), ties.rank(method="min").tolist(),
      ties.rank(method="dense").tolist(), ties.rank(method="first").tolist())

# 07. cumcount and ngroup
# ------------------------------
# - cumcount(): number of each row INSIDE its group (0, 1, 2...), in the
#   current row order. cumcount(ascending=False) counts from the end.
# - ngroup(): one integer id per group (0..G-1), in sorted key order by
#   default. Handy for labelling groups or making a compact key.
# - Together with sort_values they find "first/last event per group".

c = sales[["region", "rep"]].copy()
c["pos"] = sales.groupby("region").cumcount()
c["from_end"] = sales.groupby("region").cumcount(ascending=False)
c["group_id"] = sales.groupby("region").ngroup()
print(c)
print("\nngroup with sort=False (order of first appearance):", sales.groupby("region", sort=False).ngroup().tolist())

# 08. nth, head, tail Per Group
# ------------------------------------
# - head(n) / tail(n): first / last n rows of each group, in the original
#   row order, with the original index (a filter, not an aggregation).
# - nth(k) / nth([0, -1]): the k-th row (negative counts from the end).
# - In pandas 2.x nth behaves like a filter (keeps the original index), not
#   like an aggregation with group keys as index.
# - They use CURRENT row order: sort first if "first" must mean "earliest".

print("head(1) per region:\n", sales.groupby("region").head(1)[["region", "rep"]], sep="")
print("\ntail(1) per region index:", sales.groupby("region").tail(1).index.tolist())
print("nth(1) index:", sales.groupby("region").nth(1).index.tolist())
print("nth([0, -1]) index:", sales.groupby("region").nth([0, -1]).index.tolist())
print("Best row per group via sort + head:\n",
      sales.sort_values("revenue", ascending=False).groupby("region").head(1)[["region", "rep", "revenue"]], sep="")

# 09. rolling - Windows, min_periods, center
# ------------------------------------------------
# - s.rolling(window=3).mean(): average over the last 3 values.
# - The first window-1 results are NaN because there are not enough values.
# - min_periods=1 starts producing results as soon as 1 value exists.
# - center=True puts the label in the middle of the window.
# - Works for sum, mean, std, min, max, median, count, var, quantile...
# - Grouped rolling: df.groupby("k")["v"].rolling(3).mean() adds the group
#   key to the index; use droplevel(0) to line up with the original rows.

x = pd.Series([1, 2, 4, 8, 16, 32], dtype=float)
print("rolling(3).mean():           ", x.rolling(3).mean().tolist())
print("rolling(3, min_periods=1):   ", x.rolling(3, min_periods=1).mean().tolist())
print("rolling(3, center=True):     ", x.rolling(3, center=True).mean().tolist())
print("rolling(3).sum() with NaN inside:", pd.Series([1, np.nan, 3, 4]).rolling(2).sum().tolist())
print("... min_periods=1:               ", pd.Series([1, np.nan, 3, 4]).rolling(2, min_periods=1).sum().tolist())

grp = pd.DataFrame({"k": list("aaabbb"), "v": [1.0, 2, 3, 10, 20, 30]})
roll = grp.groupby("k")["v"].rolling(2).mean()
print("\nGrouped rolling index levels:", roll.index.names)
grp["roll2"] = roll.droplevel(0)
print(grp)

# 10. rolling With closed= and Time-Based Windows
# -----------------------------------------------------
# - closed controls which window ends are included: "right" (default: the
#   current row is included), "left" (current row excluded: good to avoid
#   look-ahead leakage), "both", "neither".
# - With a DatetimeIndex, window="3D" means a calendar span, not a row
#   count, so uneven dates work correctly. (Time windows are right-closed
#   by default.)
# - GOTCHA: with a time window and gaps, windows can have very few rows.

print("closed='right':  ", x.rolling(3, closed="right").sum().tolist())
print("closed='left':   ", x.rolling(3, closed="left").sum().tolist())
print("closed='both':   ", x.rolling(3, closed="both").sum().tolist())
print("closed='neither':", x.rolling(3, closed="neither", min_periods=1).sum().tolist())

ts = pd.Series([1.0, 2, 3, 4], index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-05", "2024-01-06"]))
print("\n2D window sum (calendar based):", ts.rolling("2D").sum().tolist())
print("2D window count:               ", ts.rolling("2D").count().tolist())
print("2D window, closed='left':      ", ts.rolling("2D", closed="left").sum().tolist())

# 11. rolling apply
# ----------------------
# - rolling(n).apply(func, raw=True) runs your function per window.
#   raw=True passes a plain NumPy array (much faster than a Series).
# - Use it only for things pandas lacks (range, custom weights, mode).
#   Built-ins (mean, std, ...) are much faster.
# - engine="numba" can speed it up, but needs numba installed (not used here).

rng_win = x.rolling(3).apply(lambda w: w.max() - w.min(), raw=True)
print("rolling range:", rng_win.tolist())
weights = np.array([0.2, 0.3, 0.5])
print("weighted avg: ", x.rolling(3).apply(lambda w: np.dot(w, weights), raw=True).round(2).tolist())

# 12. expanding and ewm
# -----------------------------
# - expanding(): window grows from the first row to the current row
#   (running mean, running max). min_periods works the same way.
# - ewm: exponentially weighted: recent values count more.
#   span, com, halflife or alpha set the decay.
# - adjust=True (default) uses exact weights from the start;
#   adjust=False uses the recursive formula  y = (1-a)*y_prev + a*x.
# - ewm results at early rows differ between the two settings.

print("expanding mean:", x.expanding().mean().round(2).tolist())
print("expanding max: ", x.expanding().max().tolist())
print("expanding(min_periods=3).mean():", x.expanding(min_periods=3).mean().round(2).tolist())
print("ewm(alpha=0.5).mean():              ", x.ewm(alpha=0.5).mean().round(2).tolist())
print("ewm(alpha=0.5, adjust=False).mean():", x.ewm(alpha=0.5, adjust=False).mean().round(2).tolist())
print("ewm(span=3) alpha equals 2/(3+1):", np.isclose(x.ewm(span=3).mean().iloc[-1], x.ewm(alpha=0.5).mean().iloc[-1]))

# 13. Cumulative Ops, diff, pct_change
# -------------------------------------------
# - cumsum, cumprod, cummax, cummin: running totals; NaN stays NaN but
#   does not stop the running value (skipna=True).
# - diff(n): difference with the row n steps before. First n rows NaN.
# - pct_change(): relative change. In pandas 2.2 write fill_method=None so
#   missing values are NOT forward-filled silently (the old default warns).
# - Inside groupby, they restart per group and avoid leaking across groups.

p = pd.Series([100.0, 110, np.nan, 121, 133.1])
print("cumsum:", p.cumsum().tolist())
print("cummax:", p.cummax().tolist())
print("diff:  ", p.diff().tolist())
print("pct_change(fill_method=None):", p.pct_change(fill_method=None).round(3).tolist())

by_region = sales.groupby("region")["revenue"]
d = sales[["region", "revenue"]].copy()
d["cum_rev"] = by_region.cumsum().round(1)
d["diff_prev"] = by_region.diff().round(1)
d["chg"] = by_region.pct_change(fill_method=None).round(2)
print("\nPer group (restarts at each region):\n", d.sort_values("region", kind="stable"), sep="")

# 14. pipe, assign and Method Chaining
# -------------------------------------------
# - Method chaining: write a pipeline as one expression, one step per line,
#   inside brackets. Reads top to bottom like a recipe, with no temporary
#   variables.
# - assign(new=lambda d: ...) adds columns; the lambda sees the frame as it
#   is at that point in the chain.
# - query("...") filters; rename, astype, sort_values, reset_index all
#   return new frames and chain well.
# - pipe(func, *args) puts YOUR function in the chain: func(df, *args).
# - Avoid inplace=True in chains (it returns None and breaks the chain).
# - Keep chains readable: if one gets longer than ~10 steps, split it.

def add_share(df, col, by):
    return df.assign(share=df[col] / df.groupby(by)[col].transform("sum"))

result = (
    sales
    .query("units >= 5")
    .assign(price=lambda d: (d["revenue"] / d["units"]).round(2))
    .pipe(add_share, "revenue", "region")
    .assign(share=lambda d: d["share"].round(3))
    .sort_values(["region", "share"], ascending=[True, False])
    .reset_index(drop=True)
    .loc[:, ["region", "rep", "price", "share"]]
)
print(result.head(6))

# 15. crosstab
# ----------------
# - pd.crosstab(rows, cols) counts how often each pair of values appears:
#   a frequency table (a pivot_table with count as default).
# - values= with aggfunc= aggregates a column instead of counting.
# - margins=True adds totals. normalize="index"/"columns"/"all" gives
#   proportions (rows add to 1 with "index").
# - Inputs can be Series, so it works without a DataFrame.
# - Missing combinations show 0 (not NaN) for counts.

big_sales = sales.assign(size=np.where(sales["units"] >= 8, "big", "small"))
print("counts with margins:\n", pd.crosstab(big_sales["region"], big_sales["size"], margins=True), sep="")
print("\nrow proportions:\n", pd.crosstab(big_sales["region"], big_sales["size"], normalize="index").round(2), sep="")
print("\nsum of revenue:\n", pd.crosstab(big_sales["region"], big_sales["size"], values=big_sales["revenue"], aggfunc="sum").round(1), sep="")

# 16. merge_asof
# -------------------
# - merge_asof matches each left row to the NEAREST key on the right
#   (not the exact one): a "last known value" join. Typical use: attach
#   the most recent price/quote/rate to each trade or event.
# - BOTH frames must be sorted by the key, or it raises ValueError.
# - direction: "backward" (default, last value at or before), "forward",
#   "nearest".
# - tolerance=: maximum allowed distance; farther matches become NaN.
# - by="symbol" matches only within the same group.
# - allow_exact_matches=False forbids equal keys.

trades = pd.DataFrame({
    "time": pd.to_datetime(["2024-01-01 10:00:05", "2024-01-01 10:00:25", "2024-01-01 10:01:10", "2024-01-01 10:00:40"]),
    "sym": ["A", "A", "A", "B"],
    "qty": [10, 20, 30, 5],
}).sort_values("time")
quotes = pd.DataFrame({
    "time": pd.to_datetime(["2024-01-01 10:00:00", "2024-01-01 10:00:20", "2024-01-01 10:01:00", "2024-01-01 10:00:30"]),
    "sym": ["A", "A", "A", "B"],
    "price": [50.0, 51.0, 52.0, 9.0],
}).sort_values("time")
print("backward, by sym:\n", pd.merge_asof(trades, quotes, on="time", by="sym"), sep="")
print("\nwith tolerance 8s (some become NaN):\n",
      pd.merge_asof(trades, quotes, on="time", by="sym", tolerance=pd.Timedelta("8s"))["price"].tolist(), sep="")
print("direction='forward':", pd.merge_asof(trades, quotes, on="time", by="sym", direction="forward")["price"].tolist())
try:
    pd.merge_asof(trades.sort_values("qty", ascending=False), quotes, on="time", by="sym")
except ValueError as e:
    print("unsorted left ->", e)

# 17. merge indicator and validate
# -----------------------------------------
# - indicator=True adds a column _merge: "both", "left_only", "right_only".
#   Great for finding rows that did not match.
# - indicator="source" names the column yourself.
# - validate checks the key relationship and raises MergeError if wrong:
#   "one_to_one", "one_to_many", "many_to_one", "many_to_many".
# - Duplicated keys on the side you thought was unique silently multiply
#   rows; validate turns that into a loud error.
# - suffixes=("_x","_y") names overlapping non-key columns.

emp = pd.DataFrame({"id": [1, 2, 3], "name": ["Ann", "Bo", "Cy"]})
dept = pd.DataFrame({"id": [2, 3, 4], "dept": ["HR", "IT", "Ops"]})
m = emp.merge(dept, on="id", how="outer", indicator="source")
print(m)
print("Unmatched left rows:", m.loc[m["source"] == "left_only", "name"].tolist())

dupe = pd.DataFrame({"id": [2, 2], "dept": ["HR", "IT"]})
print("Without validate rows:", len(emp.merge(dupe, on="id")), "(row for id=2 doubled)")
try:
    emp.merge(dupe, on="id", validate="one_to_one")
except pd.errors.MergeError as e:
    print("validate='one_to_one' ->", type(e).__name__)
print("validate='one_to_many' passes:", len(emp.merge(dupe, on="id", validate="one_to_many")))

# 18. explode
# ----------------
# - explode turns each item of a list-like cell into its own row; other
#   columns are repeated. Empty lists and NaN give one NaN row.
# - Result keeps the original index (duplicates!). Use ignore_index=True
#   or reset_index afterwards.
# - explode on several columns at once needs equal list lengths per row.
# - Reverse: groupby + agg(list). Result dtype is object, so cast with
#   astype after exploding if you need numbers.

tags = pd.DataFrame({"post": ["p1", "p2", "p3"], "tags": [["py", "pd"], ["np"], []], "n": [1, 2, 3]})
ex = tags.explode("tags")
print(ex)
print("index is duplicated:", ex.index.tolist(), "| ignore_index:", tags.explode("tags", ignore_index=True).index.tolist())
print("dtype after explode:", ex["tags"].dtype)
print("count per tag:", ex["tags"].value_counts().to_dict())
both = pd.DataFrame({"a": [[1, 2], [3]], "b": [["x", "y"], ["z"]]}).explode(["a", "b"], ignore_index=True)
print("explode two columns:\n", both, sep="")
print("rebuild lists:", ex.dropna(subset=["tags"]).groupby("post")["tags"].agg(list).to_dict())

# 19. combine_first and clip
# ---------------------------------
# - a.combine_first(b): take a's values, and where a is NaN (or the label
#   is missing) use b's. Result index/columns are the union. Good for
#   patching a main table from a backup source.
# - fillna(b) is similar but keeps a's index only (does not add rows).
# - clip(lower, upper) caps values to a range: outlier control (winsorising).
#   Bounds can be Series (per-row) too.
# - update() modifies in place and ignores NaN in the source.

main = pd.DataFrame({"x": [1.0, np.nan, 3.0]}, index=["a", "b", "c"])
backup = pd.DataFrame({"x": [10.0, 20.0, 30.0, 40.0]}, index=["a", "b", "c", "d"])
print("combine_first:\n", main.combine_first(backup), sep="")
print("fillna(backup) keeps only a,b,c:", main["x"].fillna(backup["x"]).index.tolist())
vals = pd.Series([-5, 0, 7, 15, 40])
print("clip(0, 10):", vals.clip(0, 10).tolist(), "| clip(upper=10):", vals.clip(upper=10).tolist())
lo, hi = vals.quantile(0.1), vals.quantile(0.9)
print("winsorise at 10%/90%:", vals.clip(lo, hi).round(1).tolist())

# 20. nlargest, nsmallest, describe Tweaks and Sampling
# -----------------------------------------------------------
# - nlargest(n, columns) / nsmallest: top/bottom n rows (faster than a full
#   sort when n is small). keep="first"/"last"/"all" handles ties.
# - Inside groupby: g["col"].nlargest(2) returns a MultiIndex Series.
# - describe(percentiles=[...]) picks percentiles; include="all" mixes
#   numbers and text; include=["object"]; exclude=... filters dtypes.
# - sample(n=, frac=, random_state=, weights=, replace=): random rows.
#   ALWAYS pass random_state for repeatable results.
# - Per-group sampling: groupby(...).sample(n=1, random_state=0).
# - GOTCHA: sample(frac=0.5) after sorting returns a shuffled order too;
#   sort_index() if you want the original order back.

print("nlargest(3, 'revenue'):\n", sales.nlargest(3, "revenue")[["rep", "revenue"]], sep="")
print("\nnsmallest(2, ['units']) keep='all':", sales.nsmallest(2, "units", keep="all").index.tolist())
print("top 2 revenue per region:\n", sales.groupby("region")["revenue"].nlargest(2).round(1), sep="")
print("\ndescribe with custom percentiles:\n", sales["revenue"].describe(percentiles=[0.1, 0.5, 0.9]).round(2), sep="")
print("\ndescribe(include='all') columns:", list(sales.describe(include="all").columns))
print("describe(include=['object']):\n", sales.describe(include=["object"]), sep="")
print("\nsample(3, random_state=0) index:", sales.sample(3, random_state=0).index.tolist())
print("sample(frac=0.3, random_state=1) rows:", len(sales.sample(frac=0.3, random_state=1)))
print("weighted sample picks the heavy row:", sales.sample(1, weights=[0] * 9 + [1], random_state=0).index.tolist())
print("one random row per region:\n", sales.groupby("region").sample(1, random_state=0)[["region", "rep"]], sep="")

print("\n# End of Advanced GroupBy, Window and Method Chaining")
