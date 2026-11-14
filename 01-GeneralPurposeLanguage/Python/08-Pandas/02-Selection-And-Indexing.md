# Selection and Indexing — Notes

## What this covers
The different ways to pull columns out of a DataFrame, the label-vs-position distinction between `.loc[]` and `.iloc[]`, fast scalar access, boolean filtering, and the classic `SettingWithCopyWarning` trap.

## Key points
- `df['col']` returns a Series; `df[['c1','c2']]` (double brackets — a list inside the indexer) returns a DataFrame; `df.col` is attribute access that only works for identifier-safe, non-colliding, single column names.
- Bracket-with-list is the only form safe for multiple or **dynamic** (variable) column names — you can't do `df.col1,col2` and you can't pass a variable to dot access.
- `.loc[]` is **label**-based and slices are **inclusive** of the end label; `.iloc[]` is **position**-based (like list slicing) and slices **exclude** the end position. This is the single most important distinction in pandas.
- `.at[row, col]` / `.iat[pos, pos]` fetch a single scalar faster than `.loc`/`.iloc` because they skip the general-purpose indexing machinery.
- Boolean filtering: `df['col'] > x` builds a boolean mask Series; `df[mask]` keeps the True rows.
- Combine conditions with `&`, `|`, `~` — not Python's `and`/`or`/`not` — and wrap each condition in parentheses because `&` binds tighter than comparison operators.
- `SettingWithCopyWarning`: `df[mask]['col'] = value` is chained indexing through an intermediate object pandas may or may not have copied — the fix is one `.loc[mask, 'col'] = value` call.

## Gotchas (the part worth revising twice)
- Python's `and`/`or` call `bool()` on their operand; a multi-element Series has no single truth value, so this raises `ValueError: The truth value of a Series is ambiguous` — always use `&`/`|` for elementwise logic.
- `orders.loc['a':'c']` and `orders.iloc[0:2]` can look like "the same slice" at a glance but return different row counts — inclusive label slicing vs exclusive position slicing catches almost everyone at least once.
- Chained indexing (`df[mask]['col'] = value`) may silently fail to update the original DataFrame — pandas can't guarantee the first `[]` returned a view rather than a copy. Always assign through a single `.loc[]`/`.iloc[]` call.
- A column named the same as a DataFrame method or attribute (`count`, `shape`, ...) shadows it under dot access — another reason to default to `df['col']`.

## When it matters
Filtering rows and pulling subsets is the most common operation in any data-cleaning or analysis script — getting `.loc` vs `.iloc` wrong silently returns the wrong rows instead of erroring, and ignoring the copy warning silently drops edits.

## One-line recap example
```python
import pandas as pd
df = pd.DataFrame({"amt": [10, 250, 40]}, index=["a", "b", "c"])
df.loc[df["amt"] > 100, "amt"] = 0   # correct, in-place, no warning
```
