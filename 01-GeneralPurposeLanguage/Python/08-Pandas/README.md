# 08 - Pandas

| File | Covers |
|---|---|
| [01-Series-And-DataFrame-Basics](01-Series-And-DataFrame-Basics.ipynb) | Creating Series/DataFrame, core attributes, `.info()`/`.describe()` |
| [02-Selection-And-Indexing](02-Selection-And-Indexing.ipynb) | `.loc` vs `.iloc`, `.at`/`.iat`, boolean masks, `SettingWithCopyWarning` |
| [03-Data-Cleaning](03-Data-Cleaning.ipynb) | Missing data, duplicates, type conversion, `.str` accessor |
| [04-Data-Transformation](04-Data-Transformation.ipynb) | `.apply()`/`.map()`, vectorized vs apply performance, sorting, `value_counts` |
| [05-GroupBy-And-Aggregation](05-GroupBy-And-Aggregation.ipynb) | Split-apply-combine, `.agg()`/`.transform()`, `pivot_table()` |
| [06-Merging-And-Joining](06-Merging-And-Joining.ipynb) | `merge()` (inner/left/right/outer), `.join()`, `pd.concat()` |
| [07-Reshaping](07-Reshaping.ipynb) | Wide vs long, `.pivot()` vs `.pivot_table()`, `.melt()`, `.stack()`/`.unstack()` |
| [08-Time-Series](08-Time-Series.ipynb) | `DatetimeIndex`, `.resample()`, `.rolling()`, `.shift()`, timezones |
| [09-Input-Output](09-Input-Output.ipynb) | CSV/JSON/Excel/SQL read-write round trips |
| [10-Performance-And-Best-Practices](10-Performance-And-Best-Practices.ipynb) | Vectorized vs apply vs iterrows, memory optimization, method chaining |
| [11-MultiIndex-And-Advanced-Indexing](11-MultiIndex-And-Advanced-Indexing.ipynb) | `MultiIndex`, `IndexSlice`, `xs`, level ops, index alignment, `reindex`, `IntervalIndex`, `cut`/`qcut`, `query`/`eval`, `where`/`mask` |
| [12-Dtypes-Categorical-And-Nullable](12-Dtypes-Categorical-And-Nullable.ipynb) | `category`, nullable `Int64`/`string`/`boolean`, `pd.NA` logic, `convert_dtypes`, downcasting, memory, pyarrow dtypes, copy-on-write |
| [13-Advanced-GroupBy-Window-And-Method-Chaining](13-Advanced-GroupBy-Window-And-Method-Chaining.ipynb) | `transform`/`filter`/`apply`, named aggregation, rank, rolling/expanding/ewm, `pipe`, method chaining, `crosstab`, `merge_asof`, `explode` |
| [14-Text-And-Datetime-Deep-Dive](14-Text-And-Datetime-Deep-Dive.ipynb) | `.str` regex tools, `extract`, `get_dummies`, `.dt` accessor, `Period`, offsets, time zones and DST, `resample` options, messy date parsing |
| [15-End-To-End-Data-Analysis](15-End-To-End-Data-Analysis.ipynb) | full workflow on synthetic data: clean, validate, merge, KPIs, cohorts, outliers, pipelines, plus pandas anti-patterns with fixes |

Each notebook starts with a plain-English cheat sheet for revision.
