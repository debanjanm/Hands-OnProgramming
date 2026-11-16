# MultiIndex and Advanced Indexing — Notes

## What this covers
Hierarchical (MultiIndex) rows, slicing them with `.loc`, `pd.IndexSlice` and `xs`, reordering and sorting levels, `set_index`/`reset_index`, grouping by levels, label alignment in arithmetic, `reindex`/`align`, duplicate labels, `RangeIndex`/`IntervalIndex`, `pd.cut`/`pd.qcut`, and the filtering helpers `isin`, `between`, `query`, `eval`, `where`, `mask`, `filter`. Basic `loc`/`iloc` is in 02, groupby basics in 05, reshaping in 07.

## Key points
- Build a MultiIndex with `from_tuples` (pairs), `from_product` (full grid), `from_arrays` (one list per level) or `from_frame`. Always set `names=`.
- `df.loc["East"]` picks the outer level; `df.loc[("East", "Q2")]` picks one row; `df.loc[pd.IndexSlice[:, "Q1":"Q2"], :]` slices an inner level.
- `df.xs("Q1", level="quarter")` picks by any level without IndexSlice. It drops that level unless `drop_level=False`.
- A MultiIndex stores `.levels` (unique labels) and `.codes` (integer pointers). `get_level_values(name)` returns the full-length labels of one level.
- `swaplevel` / `reorder_levels` change level order but do not sort rows; follow with `sort_index()`.
- `set_index([...])` makes columns into levels; `reset_index()` brings them back (`level=` for one, `drop=True` to discard).
- `groupby(level="region")` groups by an index level directly, no reset needed.
- Arithmetic aligns by LABEL. `.add(other, fill_value=0)` handles one-sided labels.
- `reindex` re-selects rows to match a new label list (missing become NaN, `method="ffill"` fills gaps on sorted index); `reindex_like` copies another object's index; `align` puts two objects on a common index.
- `RangeIndex` is the default and costs almost no memory. Filtering keeps old labels, so `.loc` and `.iloc` start to disagree.
- `pd.cut` makes bins by edges (right-closed by default); `pd.qcut` makes bins with equal counts; `IntervalIndex` supports lookups by value.
- `isin`, `between`, `query("a > @x")`, `eval`, `where` (keep where True), `mask` (replace where True), `filter(like=/regex=/items=)` cover most filtering needs.

## Gotchas (the part worth revising twice)
- Slicing a range on an unsorted MultiIndex raises `UnsortedIndexError`. Sort first with `sort_index()`.
- After filtering rows, `.levels` still lists removed labels. Use `remove_unused_levels()` when you read levels.
- `a + b` on Series with different labels gives NaN for the labels that do not match, silently. Same length does not mean matched by position.
- Duplicate labels make `.loc["a"]` return a Series instead of a scalar, and `reindex` fails. Check `index.is_unique`; guard with `set_flags(allows_duplicate_labels=False)`.
- `pd.cut` with right-closed bins turns the lowest edge value into NaN unless `include_lowest=True`.
- `where` fills with NaN by default, which turns integer columns into floats.
- Use `&`, `|`, `~` with brackets around each condition. `and`/`or` raise "truth value is ambiguous".
- `query` is a mini-language, not full Python; use `@var` for outside variables and backticks for names with spaces.

## When it matters
Any time data has natural hierarchy (region/quarter, country/city, store/product), or when you join, subtract or compare two objects and the result must line up on labels. Understanding alignment and sorted indexes prevents the silent NaN and wrong-row bugs that are hardest to spot.

## One-line recap example
```python
import pandas as pd
s = pd.Series([1, 2, 3, 4], index=pd.MultiIndex.from_product([["E", "W"], ["Q1", "Q2"]], names=["r", "q"]))
s.loc[pd.IndexSlice[:, "Q1"]]  # all regions, only Q1 (index is sorted, so slicing is safe)
```
