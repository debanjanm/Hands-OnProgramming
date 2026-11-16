# 01. Building a MultiIndex
# 02. Slicing a MultiIndex with .loc and pd.IndexSlice
# 03. xs - Cross-Section by Level
# 04. levels, codes, names - What Is Inside
# 05. swaplevel, reorder_levels, sort_index
# 06. set_index and reset_index
# 07. stack and unstack Recap
# 08. groupby on Index Levels
# 09. Index Alignment on Arithmetic (Classic Gotcha)
# 10. reindex, reindex_like, align
# 11. Duplicate Index Problems
# 12. RangeIndex
# 13. IntervalIndex, pd.cut, pd.qcut
# 14. isin and between
# 15. query and eval
# 16. where and mask
# 17. .filter - Select Labels by Pattern
# 18. Boolean Masks Combined With Index Levels
#
# See also: 02-Selection-And-Indexing (loc/iloc basics), 05-GroupBy-And-Aggregation,
# 07-Reshaping (pivot/melt/stack basics).

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

# 01. Building a MultiIndex
# ----------------------------
# - A MultiIndex is an index with 2+ levels: every row label is a tuple.
# - from_tuples: you already have a list of (a, b) pairs.
# - from_product: all combinations of several lists (a full grid).
# - from_arrays: one list per level, same length, matched by position.
# - from_frame: take columns of a DataFrame as levels.
# - Always give names= so you can refer to levels by name later.

t = pd.MultiIndex.from_tuples([("East", "Q1"), ("East", "Q2"), ("West", "Q1")], names=["region", "quarter"])
print("from_tuples:\n", t, sep="")

p = pd.MultiIndex.from_product([["East", "West"], ["Q1", "Q2", "Q3"]], names=["region", "quarter"])
print("\nfrom_product (2 x 3 = 6 rows):", len(p))

a = pd.MultiIndex.from_arrays([["East", "East", "West"], [1, 2, 1]], names=["region", "n"])
print("from_arrays:", a.tolist())

f = pd.MultiIndex.from_frame(pd.DataFrame({"x": ["a", "b"], "y": [1, 2]}))
print("from_frame names:", f.names)

df = pd.DataFrame({"sales": rng.integers(10, 100, 6), "cost": rng.integers(5, 50, 6)}, index=p)
print("\nDataFrame with MultiIndex rows:\n", df, sep="")

# 02. Slicing a MultiIndex with .loc and pd.IndexSlice
# --------------------------------------------------------
# - df.loc["East"] picks the outer level and drops it from the result.
# - df.loc[("East", "Q2")] (a tuple) picks one exact row.
# - To slice the INNER level you need pd.IndexSlice: idx[:, "Q1":"Q2"].
# - Slicing ranges on a MultiIndex needs it to be SORTED (lexsorted),
#   otherwise pandas raises UnsortedIndexError.
# - Always pass axis info clearly: df.loc[idx[...], :] is safest.

idx = pd.IndexSlice
print("df.loc['East']:\n", df.loc["East"], sep="")
print("\ndf.loc[('East', 'Q2')]:\n", df.loc[("East", "Q2")], sep="")
print("\ndf.loc[idx[:, 'Q1':'Q2'], :] (inner level range, all regions):\n", df.loc[idx[:, "Q1":"Q2"], :], sep="")
print("\ndf.loc[idx[:, ['Q1', 'Q3']], 'sales'] (list of inner labels):\n", df.loc[idx[:, ["Q1", "Q3"]], "sales"], sep="")

shuffled = df.iloc[[3, 0, 5, 1, 4, 2]]
print("\nIs shuffled index sorted?", shuffled.index.is_monotonic_increasing)
try:
    shuffled.loc[idx["East":"West", "Q1":"Q2"], :]
except Exception as e:
    print("Range slice on unsorted MultiIndex ->", type(e).__name__)
print("After sort_index it works:", shuffled.sort_index().loc[idx[:, "Q1":"Q2"], :].shape)

# 03. xs - Cross-Section by Level
# ----------------------------------
# - df.xs(key, level=...) selects by one level's value, ANYWHERE in the
#   hierarchy, without needing IndexSlice.
# - By default xs DROPS the level it matched; drop_level=False keeps it.
# - It is a shortcut for the common "give me all Q1 rows" question.

print("df.xs('Q1', level='quarter'):\n", df.xs("Q1", level="quarter"), sep="")
print("\nSame with drop_level=False:\n", df.xs("Q1", level="quarter", drop_level=False), sep="")
print("\nColumn-wise xs on a Series-like: xs(('West','Q2')):\n", df.xs(("West", "Q2")), sep="")

# 04. levels, codes, names - What Is Inside
# ----------------------------------------------
# - A MultiIndex stores each level as a list of UNIQUE labels (.levels) and
#   the rows as integer pointers into them (.codes). This saves memory.
# - get_level_values(n or name) gives the full-length labels of one level.
# - GOTCHA: .levels can still contain labels that are no longer in the data
#   after you filter rows. Use remove_unused_levels() to clean up.

print("levels:", [list(l) for l in df.index.levels])
print("codes: ", [list(c) for c in df.index.codes])
print("names: ", df.index.names, " nlevels:", df.index.nlevels)
print("get_level_values('quarter'):", list(df.index.get_level_values("quarter")))

east_only = df.loc[["East"]]
print("\nAfter filtering to East only, region level still lists:", list(east_only.index.levels[0]))
print("After remove_unused_levels:", list(east_only.index.remove_unused_levels().levels[0]))

# 05. swaplevel, reorder_levels, sort_index
# ---------------------------------------------
# - swaplevel(i, j) swaps two levels; reorder_levels([...]) sets full order.
# - Neither sorts the rows. Call sort_index afterwards, or slicing can fail.
# - sort_index(level="quarter") sorts by one level; sort_remaining=False
#   leaves the other levels in their current order.

sw = df.swaplevel("region", "quarter")
print("swaplevel (rows NOT re-sorted):\n", sw, sep="")
print("\nswaplevel + sort_index:\n", sw.sort_index(), sep="")
print("\nreorder_levels(['quarter','region']).sort_index().head(3):\n",
      df.reorder_levels(["quarter", "region"]).sort_index().head(3), sep="")
print("\nsort_index(level='quarter', sort_remaining=False).head(4):\n",
      df.sort_index(level="quarter", sort_remaining=False).head(4), sep="")

# 06. set_index and reset_index
# ---------------------------------
# - set_index(["a", "b"]) turns columns into MultiIndex levels.
# - reset_index() turns ALL levels back into columns; level="b" only that one.
# - reset_index(drop=True) throws the index away instead of keeping it.
# - set_index returns a new frame; the original is untouched (no inplace).

flat = pd.DataFrame({"region": ["E", "E", "W"], "quarter": ["Q1", "Q2", "Q1"], "sales": [5, 6, 7]})
mi = flat.set_index(["region", "quarter"])
print("set_index(['region','quarter']):\n", mi, sep="")
print("\nreset_index(level='quarter'):\n", mi.reset_index(level="quarter"), sep="")
print("\nreset_index(drop=True):\n", mi.reset_index(drop=True), sep="")

# 07. stack and unstack Recap
# -------------------------------
# - unstack moves an index level into columns; stack does the reverse.
# - Missing combinations become NaN after unstack; fill_value= fixes that.
# - Full details are in 07-Reshaping; here they are tools for MultiIndex.

s = df["sales"]
wide = s.unstack("quarter")
print("unstack('quarter'):\n", wide, sep="")
print("\nunstack(0) (outer level to columns):\n", s.unstack(0), sep="")
print("\nstack() back gives a Series again:", wide.stack().shape)
partial = s.drop(("West", "Q3"))
print("\nMissing combo -> NaN:\n", partial.unstack("quarter"), sep="")
print("\nfill_value=0:\n", partial.unstack("quarter", fill_value=0), sep="")

# 08. groupby on Index Levels
# -------------------------------
# - groupby(level="region") groups by an index level, no reset_index needed.
# - Level can be a name, a number, or a list of them.
# - Aggregations like .sum(level=...) were removed; always use groupby.

print("groupby(level='region').sum():\n", df.groupby(level="region").sum(), sep="")
print("\ngroupby(level=['region','quarter']).sum() keeps full detail:", df.groupby(level=[0, 1]).sum().shape)
print("\nMix a level and a column: use pd.Grouper(level=...) or reset_index first")
print(df.groupby([pd.Grouper(level="region"), df["sales"] > 50]).size())

# 09. Index Alignment on Arithmetic (Classic Gotcha)
# -------------------------------------------------------
# - Arithmetic between Series/DataFrames MATCHES BY LABEL, not by position.
# - Labels present in only one side give NaN. This is a silent surprise.
# - Fix choices: .add(other, fill_value=0), or use .to_numpy()/.values when
#   you truly want position-based math (and lengths must match).
# - Duplicate labels make alignment even stranger (see section 11).

a = pd.Series([1, 2, 3], index=["x", "y", "z"])
b = pd.Series([10, 20, 30], index=["y", "z", "w"])
print("a + b (label-matched):\n", a + b, sep="")
print("\na.add(b, fill_value=0):\n", a.add(b, fill_value=0), sep="")
c = pd.Series([100, 200, 300])
print("\nPosition-based (ignoring labels): a.to_numpy() + c.to_numpy() =", a.to_numpy() + c.to_numpy())
print("Same-length but different labels with a + c:\n", a + c, sep="")

d1 = pd.DataFrame({"u": [1, 2], "v": [3, 4]}, index=["r1", "r2"])
d2 = pd.DataFrame({"v": [10, 20], "w": [5, 6]}, index=["r2", "r3"])
print("\nDataFrame + DataFrame aligns BOTH rows and columns:\n", d1 + d2, sep="")

# 10. reindex, reindex_like, align
# ------------------------------------
# - reindex(new_labels) conforms to a new label list: missing -> NaN,
#   labels not listed are dropped. It does NOT rename; it re-selects.
# - method="ffill"/"bfill" fills gaps only when the index is monotonic.
# - reindex_like(other) copies another object's index (and columns).
# - align(other, join="outer") gives both objects on a common index.
# - GOTCHA: reindex on a duplicate index raises ValueError.

r = pd.Series([1.0, 2.0, 3.0], index=[10, 20, 30])
print("reindex([10, 15, 30, 40]):\n", r.reindex([10, 15, 30, 40]), sep="")
print("\nreindex with method='ffill':\n", r.reindex([10, 15, 30, 40], method="ffill"), sep="")
print("\nreindex with fill_value=0:", r.reindex([10, 15], fill_value=0).tolist())

other = pd.Series([0, 0, 0, 0], index=[30, 20, 40, 10])
print("\nreindex_like(other).index:", r.reindex_like(other).index.tolist())

left, right = r.align(other, join="outer")
print("align outer -> left:", left.tolist(), " right:", right.tolist())
left, right = r.align(other, join="inner")
print("align inner -> shared labels:", left.index.tolist())

try:
    pd.Series([1, 2], index=["a", "a"]).reindex(["a", "b"])
except ValueError as e:
    print("reindex with duplicate index ->", e)

# 11. Duplicate Index Problems
# --------------------------------
# - pandas allows duplicate labels. That is useful sometimes, risky mostly.
# - .loc["a"] returns a Series/DataFrame (many rows) instead of one value,
#   so the return TYPE depends on the data: a nasty source of bugs.
# - Check with index.is_unique and index.duplicated().
# - flags.allows_duplicate_labels = False makes pandas raise on duplicates.
# - Fix: reset_index, groupby-aggregate duplicates, or de-dupe on purpose.

dup = pd.Series([1, 2, 3], index=["a", "a", "b"])
print("dup.index.is_unique:", dup.index.is_unique)
print("dup.index.duplicated():", dup.index.duplicated().tolist())
print("dup.loc['a'] returns:\n", dup.loc["a"], sep="")
print("dup.loc['b'] returns a scalar:", dup.loc["b"])
print("Keep first of each label:", dup[~dup.index.duplicated(keep="first")].tolist())
print("Aggregate duplicates:", dup.groupby(level=0).sum().to_dict())

strict = pd.Series([1, 2], index=["a", "b"]).set_flags(allows_duplicate_labels=False)
try:
    strict.reindex(["a", "a"])
except Exception as e:
    print("Strict flag blocked it ->", type(e).__name__)

# 12. RangeIndex
# ------------------
# - The default index is RangeIndex(start, stop, step): stored as 3 numbers,
#   not an array, so it costs almost no memory.
# - After filtering rows the labels stay (e.g. 1, 3, 4) but it is no
#   longer a RangeIndex; it becomes Index of int64.
# - reset_index(drop=True) builds a fresh RangeIndex.
# - GOTCHA: .loc[3] is a LABEL, .iloc[3] is a POSITION; after filtering
#   they refer to different rows.

base = pd.DataFrame({"v": [10, 20, 30, 40, 50]})
print("default index:", base.index)
filt = base[base["v"] > 20]
print("after filter:", filt.index.tolist(), "type:", type(filt.index).__name__)
print("filt.loc[3] ->", filt.loc[3, "v"], "  filt.iloc[0] ->", filt.iloc[0]["v"])
print("after reset_index(drop=True):", filt.reset_index(drop=True).index)
print("RangeIndex memory (bytes):", base.index.memory_usage(), " vs Index(int64) of 5:", pd.Index([0, 1, 2, 3, 4]).memory_usage())

# 13. IntervalIndex, pd.cut, pd.qcut
# --------------------------------------
# - pd.cut(values, bins) makes fixed-width/custom bins; result dtype is
#   category with Interval labels. Intervals are right-closed by default:
#   (0, 10]. right=False gives [0, 10). include_lowest=True keeps the min.
# - pd.qcut(values, q) makes bins with (about) equal COUNTS (quantiles).
# - labels=[...] replaces interval text with names.
# - pd.IntervalIndex.from_breaks and .get_indexer / .contains do lookups.
# - GOTCHA: a value exactly equal to the lowest edge is NaN under
#   right-closed bins unless include_lowest=True.

ages = pd.Series([0, 5, 18, 25, 40, 65, 90])
cut = pd.cut(ages, bins=[0, 18, 40, 100])
print("pd.cut with edges [0, 18, 40, 100]:\n", pd.DataFrame({"age": ages, "bin": cut}), sep="")
print("\ninclude_lowest=True:", pd.cut(ages, [0, 18, 40, 100], include_lowest=True).astype(str).tolist()[:2])
print("labels:", pd.cut(ages, [-1, 18, 40, 100], labels=["child", "adult", "senior"]).tolist())
print("right=False:", pd.cut(ages, [0, 18, 40, 100], right=False).astype(str).tolist())

scores = pd.Series(np.arange(1, 13))
q = pd.qcut(scores, 4, labels=["Q1", "Q2", "Q3", "Q4"])
print("\nqcut into 4 equal-count groups:", q.value_counts().sort_index().to_dict())

ii = pd.IntervalIndex.from_breaks([0, 10, 20, 30])
print("\nIntervalIndex:", ii.tolist())
print("12 falls in bucket:", ii.get_indexer([12]).tolist(), "-> ", ii[ii.get_indexer([12])[0]])
print("Series indexed by intervals, lookup of 25:", pd.Series(["low", "mid", "high"], index=ii).loc[25])

# 14. isin and between
# ------------------------
# - s.isin([...]) -> boolean mask: "value is one of these".
# - s.between(lo, hi) -> mask; inclusive="both"/"neither"/"left"/"right".
# - ~mask negates. Prefer isin over many `==` joined with `|`.
# - Index has isin too: df[df.index.isin([...])].
# - NaN is never "between" anything and isin([np.nan]) matches NaN.

city = pd.Series(["Delhi", "Pune", "Goa", "Pune", None, "Agra"])
print("isin:", city.isin(["Pune", "Goa"]).tolist())
print("~isin:", (~city.isin(["Pune", "Goa"])).tolist())
n = pd.Series([1, 5, 10, np.nan, 15])
print("between(5, 10):", n.between(5, 10).tolist())
print("between(5, 10, inclusive='neither'):", n.between(5, 10, inclusive="neither").tolist())
print("isin([np.nan]) matches NaN:", n.isin([np.nan]).tolist())
print("index.isin:", df[df.index.get_level_values("quarter").isin(["Q1"])].shape)

# 15. query and eval
# ----------------------
# - df.query("a > 5 and b == 'x'") filters with a string expression: short,
#   chainable, no repeated df[...] names.
# - Use @var to refer to a Python variable; backticks for odd column names.
# - Index levels can be used by name inside query.
# - df.eval("c = a + b") builds new columns; with numexpr installed, big
#   frames can be faster. For small data it is about readability, not speed.
# - GOTCHA: query is a mini-language, not full Python. Not every function works.

people = pd.DataFrame({"name": ["A", "B", "C", "D"], "age": [20, 35, 50, 41], "pay k": [30, 55, 90, 70]})
limit = 30
print("query('age > @limit and `pay k` < 80'):\n", people.query("age > @limit and `pay k` < 80"), sep="")
print("\nquery on index level 'region':\n", df.query("region == 'East' and sales > 0").shape, sep="")
print("\nname in list:", people.query("name in ['A', 'D']")["name"].tolist())
print("\neval creates a column (returns a new frame):\n", people.eval("pay_per_age = `pay k` / age").round(2), sep="")

# 16. where and mask
# ----------------------
# - s.where(cond, other): KEEP where cond is True, REPLACE where False.
# - s.mask(cond, other): the opposite: REPLACE where cond is True.
# - Same shape is returned (rows are not dropped, unlike boolean indexing).
# - Default replacement is NaN, which turns ints into floats.
# - np.where(cond, a, b) is the fast numpy version returning an array.

v = pd.Series([5, -3, 8, -1, 0])
print("where(v > 0):", v.where(v > 0).tolist())
print("where(v > 0, 0):", v.where(v > 0, 0).tolist())
print("mask(v < 0, 99):", v.mask(v < 0, 99).tolist())
print("np.where label:", np.where(v > 0, "pos", "non-pos").tolist())
print("DataFrame where:\n", pd.DataFrame({"a": [1, -2], "b": [-3, 4]}).where(lambda d: d > 0, other=0), sep="")

# 17. .filter - Select Labels by Pattern
# ------------------------------------------
# - df.filter(items=[...]) picks labels that exist (silently skips missing).
# - df.filter(like="sub") keeps labels containing the substring.
# - df.filter(regex="^q") keeps labels matching a regex.
# - axis=0 filters ROW labels, axis=1 (default for DataFrame) filters columns.
# - It filters LABELS, not values; for values use boolean masks or query.

cols = pd.DataFrame(np.arange(6).reshape(2, 3), columns=["q1_sales", "q2_sales", "total_cost"], index=["row_a", "row_b"])
print("filter(like='sales'):", cols.filter(like="sales").columns.tolist())
print("filter(regex='^q'):", cols.filter(regex="^q").columns.tolist())
print("filter(items=['total_cost', 'nope']):", cols.filter(items=["total_cost", "nope"]).columns.tolist())
print("filter(like='_b', axis=0):", cols.filter(like="_b", axis=0).index.tolist())

# 18. Boolean Masks Combined With Index Levels
# -------------------------------------------------
# - Use & (and), | (or), ~ (not) with PARENTHESES around each comparison;
#   Python's `and`/`or` raise "truth value is ambiguous".
# - Index-level conditions: get_level_values gives an Index you can compare.
# - Combine: mask = (level == x) & (column > y).
# - GOTCHA: precedence! `a > 1 & b < 2` is parsed wrong without brackets.

lvl = df.index.get_level_values("quarter")
mask = (lvl != "Q2") & (df["sales"] > df["sales"].median())
print("Rows not in Q2 with above-median sales:\n", df[mask], sep="")
try:
    df[(df["sales"] > 1) and (df["cost"] > 1)]
except ValueError as e:
    print("\nUsing `and` ->", type(e).__name__)

print("\n# End of MultiIndex and Advanced Indexing")
