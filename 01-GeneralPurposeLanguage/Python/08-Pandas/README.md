# 08 - Pandas

| File | Covers |
|---|---|
| [01-Series-And-DataFrame-Basics.py](01-Series-And-DataFrame-Basics.py) · [notes](01-Series-And-DataFrame-Basics.md) | Creating Series/DataFrame, core attributes, `.info()`/`.describe()` |
| [02-Selection-And-Indexing.py](02-Selection-And-Indexing.py) · [notes](02-Selection-And-Indexing.md) | `.loc` vs `.iloc`, `.at`/`.iat`, boolean masks, `SettingWithCopyWarning` |
| [03-Data-Cleaning.py](03-Data-Cleaning.py) · [notes](03-Data-Cleaning.md) | Missing data, duplicates, type conversion, `.str` accessor |
| [04-Data-Transformation.py](04-Data-Transformation.py) · [notes](04-Data-Transformation.md) | `.apply()`/`.map()`, vectorized vs apply performance, sorting, `value_counts` |
| [05-GroupBy-And-Aggregation.py](05-GroupBy-And-Aggregation.py) · [notes](05-GroupBy-And-Aggregation.md) | Split-apply-combine, `.agg()`/`.transform()`, `pivot_table()` |
| [06-Merging-And-Joining.py](06-Merging-And-Joining.py) · [notes](06-Merging-And-Joining.md) | `merge()` (inner/left/right/outer), `.join()`, `pd.concat()` |
| [07-Reshaping.py](07-Reshaping.py) · [notes](07-Reshaping.md) | Wide vs long, `.pivot()` vs `.pivot_table()`, `.melt()`, `.stack()`/`.unstack()` |
| [08-Time-Series.py](08-Time-Series.py) · [notes](08-Time-Series.md) | `DatetimeIndex`, `.resample()`, `.rolling()`, `.shift()`, timezones |
| [09-Input-Output.py](09-Input-Output.py) · [notes](09-Input-Output.md) | CSV/JSON/Excel/SQL read-write round trips |
| [10-Performance-And-Best-Practices.py](10-Performance-And-Best-Practices.py) · [notes](10-Performance-And-Best-Practices.md) | Vectorized vs apply vs iterrows, memory optimization, method chaining |
| [11-MultiIndex-And-Advanced-Indexing.py](11-MultiIndex-And-Advanced-Indexing.py) · [notes](11-MultiIndex-And-Advanced-Indexing.md) | `MultiIndex`, `IndexSlice`, `xs`, level ops, index alignment, `reindex`, `IntervalIndex`, `cut`/`qcut`, `query`/`eval`, `where`/`mask` |
| [12-Dtypes-Categorical-And-Nullable.py](12-Dtypes-Categorical-And-Nullable.py) · [notes](12-Dtypes-Categorical-And-Nullable.md) | `category`, nullable `Int64`/`string`/`boolean`, `pd.NA` logic, `convert_dtypes`, downcasting, memory, pyarrow dtypes, copy-on-write |
| [13-Advanced-GroupBy-Window-And-Method-Chaining.py](13-Advanced-GroupBy-Window-And-Method-Chaining.py) · [notes](13-Advanced-GroupBy-Window-And-Method-Chaining.md) | `transform`/`filter`/`apply`, named aggregation, rank, rolling/expanding/ewm, `pipe`, method chaining, `crosstab`, `merge_asof`, `explode` |
| [14-Text-And-Datetime-Deep-Dive.py](14-Text-And-Datetime-Deep-Dive.py) · [notes](14-Text-And-Datetime-Deep-Dive.md) | `.str` regex tools, `extract`, `get_dummies`, `.dt` accessor, `Period`, offsets, time zones and DST, `resample` options, messy date parsing |
| [15-End-To-End-Data-Analysis.py](15-End-To-End-Data-Analysis.py) · [notes](15-End-To-End-Data-Analysis.md) | full workflow on synthetic data: clean, validate, merge, KPIs, cohorts, outliers, pipelines, plus pandas anti-patterns with fixes |

Each `.py` file has a matching `.md` notes file — a plain-English cheat sheet
for revision.
