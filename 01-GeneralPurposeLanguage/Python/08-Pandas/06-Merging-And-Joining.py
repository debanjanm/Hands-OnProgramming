# 01. pd.merge() - how='inner' / 'left' / 'right' / 'outer'
# 02. Merging on Multiple Keys
# 03. suffixes= for Overlapping Column Names
# 04. .join() - Index-Based Merging
# 05. pd.concat() - axis=0 (rows) vs axis=1 (columns) and Index Alignment
# 06. Merge Types <-> SQL JOIN Cheat Sheet

import pandas as pd

# 01. pd.merge() - how='inner' / 'left' / 'right' / 'outer'
# ------------------------------------
# - pd.merge() combines two DataFrames on a shared key column, same idea as
#   a SQL JOIN. The `how=` argument controls which rows survive when a key
#   doesn't exist on both sides.
# - Left frame: employees, some with a dept_id that doesn't exist in the
#   departments table (Eve). Right frame: departments, one dept with no
#   employees at all (Legal). This asymmetry is what makes the row-count
#   differences between the four modes visible.

print("# 01. pd.merge() - how='inner' / 'left' / 'right' / 'outer'")
print("# ------------------------------------")

employees = pd.DataFrame({
    "emp_id": [1, 2, 3, 4, 5],
    "name": ["Alice", "Bob", "Carla", "Dev", "Eve"],
    "dept_id": [10, 10, 20, 20, 99],  # 99 has no matching department
})

departments = pd.DataFrame({
    "dept_id": [10, 20, 30],
    "dept_name": ["Engineering", "Sales", "Legal"],  # Legal (30) has no employees
})

print("employees:\n", employees)
print("\ndepartments:\n", departments)

inner = pd.merge(employees, departments, on="dept_id", how="inner")
print("\nhow='inner' (only dept_id present on BOTH sides) ->", len(inner), "rows:\n", inner)

left = pd.merge(employees, departments, on="dept_id", how="left")
print("\nhow='left' (all employees kept, Eve's dept_name is NaN) ->", len(left), "rows:\n", left)

right = pd.merge(employees, departments, on="dept_id", how="right")
print("\nhow='right' (all departments kept, Legal has NaN employee cols) ->", len(right), "rows:\n", right)

outer = pd.merge(employees, departments, on="dept_id", how="outer")
print("\nhow='outer' (union of both sides, NaN wherever no match) ->", len(outer), "rows:\n", outer)

print("# Row counts here: inner=4, left=5, right=4, outer=5 - inner/left keep every")
print("#   employee-department pairing that matches; outer/right also surface Legal (empty dept).")

# 02. Merging on Multiple Keys
# ------------------------------------
# - Pass a list to `on=` to require a match on ALL listed columns together -
#   useful when a single column isn't a unique enough key (e.g. year + region).

print("\n# 02. Merging on Multiple Keys")
print("# ------------------------------------")

sales = pd.DataFrame({
    "region": ["East", "East", "West", "West"],
    "year": [2023, 2024, 2023, 2024],
    "revenue": [120000, 135000, 98000, 110000],
})
targets = pd.DataFrame({
    "region": ["East", "East", "West", "West"],
    "year": [2023, 2024, 2023, 2024],
    "target": [110000, 130000, 100000, 105000],
})

multi_key_merge = pd.merge(sales, targets, on=["region", "year"], how="inner")
print("sales:\n", sales)
print("\nMerged on ['region', 'year']:\n", multi_key_merge)
print("# A single key (e.g. just 'region') would match 2023 revenue against 2024's target too -")
print("#   the multi-key merge pins down exactly one right-hand row per left-hand row.")

# 03. suffixes= for Overlapping Column Names
# ------------------------------------
# - If both frames have a same-named column that ISN'T the merge key, pandas
#   appends suffixes to disambiguate. Default is ('_x', '_y'); override with
#   suffixes= for readable output.

print("\n# 03. suffixes= for Overlapping Column Names")
print("# ------------------------------------")

q1 = pd.DataFrame({"emp_id": [1, 2, 3], "score": [88, 91, 75]})
q2 = pd.DataFrame({"emp_id": [1, 2, 3], "score": [92, 85, 80]})

default_suffix = pd.merge(q1, q2, on="emp_id")
print("Default suffixes ('_x', '_y'):\n", default_suffix)

custom_suffix = pd.merge(q1, q2, on="emp_id", suffixes=("_q1", "_q2"))
print("\nCustom suffixes=('_q1', '_q2'):\n", custom_suffix)

# 04. .join() - Index-Based Merging
# ------------------------------------
# - .join() merges on the DataFrame INDEX by default (not a column), which is
#   why it reads more naturally when your key already lives in the index.
# - `df1.join(df2)` is roughly `pd.merge(df1, df2, left_index=True, right_index=True)`.
# - .join() defaults to how='left'; merge defaults to how='inner'.

print("\n# 04. .join() - Index-Based Merging")
print("# ------------------------------------")

left_idx = pd.DataFrame({"name": ["Alice", "Bob", "Carla"]}, index=[1, 2, 3])
right_idx = pd.DataFrame({"bonus": [500, 750]}, index=[1, 3])  # emp_id 2 missing

print("left_idx:\n", left_idx)
print("\nright_idx:\n", right_idx)
print("\nleft_idx.join(right_idx)  # default how='left', joins on index:\n", left_idx.join(right_idx))
print("\nleft_idx.join(right_idx, how='inner'):\n", left_idx.join(right_idx, how="inner"))
print("# join() is just merge() specialized for index-to-index (or index-to-column via")
print("#   on=) alignment - reach for merge() when both keys are ordinary columns.")

# 05. pd.concat() - axis=0 (rows) vs axis=1 (columns) and Index Alignment
# ------------------------------------
# - concat STACKS frames rather than matching on a key.
# - axis=0 (default): stacks rows on top of each other, like SQL UNION ALL -
#   columns are matched by NAME, missing ones become NaN.
# - axis=1: stacks columns side by side, ALIGNING BY INDEX - if the indices
#   don't line up, you get NaN gaps instead of a clean row-for-row join.

print("\n# 05. pd.concat() - axis=0 (rows) vs axis=1 (columns) and Index Alignment")
print("# ------------------------------------")

batch1 = pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})
batch2 = pd.DataFrame({"id": [3, 4], "name": ["Carla", "Dev"]})

stacked_rows = pd.concat([batch1, batch2], axis=0)
print("concat axis=0 (row-wise stack):\n", stacked_rows)
print("# Note the repeated index (0,1,0,1) - pass ignore_index=True to get a fresh 0..n-1 index:")
print(pd.concat([batch1, batch2], axis=0, ignore_index=True))

extra_col = pd.DataFrame({"age": [30, 25]}, index=[0, 1])
side_by_side = pd.concat([batch1, extra_col], axis=1)
print("\nconcat axis=1 (column-wise, indices [0,1] match cleanly):\n", side_by_side)

# GOTCHA: mismatched indices on axis=1 silently produce NaN, no error raised.
mismatched_col = pd.DataFrame({"age": [40, 22]}, index=[5, 6])
misaligned = pd.concat([batch1, mismatched_col], axis=1)
print("\nGOTCHA - concat axis=1 with mismatched indices ([0,1] vs [5,6]):")
print(misaligned)
print("# Every cell is NaN-padded because concat aligns by index label, not row position -")
print("#   reset_index(drop=True) on both sides first if you actually want positional pairing.")

# 06. Merge Types <-> SQL JOIN Cheat Sheet
# ------------------------------------
print("\n# 06. Merge Types <-> SQL JOIN Cheat Sheet")
print("# ------------------------------------")
print("# pandas how='inner'  <-> SQL INNER JOIN   (only matching keys on both sides)")
print("# pandas how='left'   <-> SQL LEFT JOIN    (all left rows, right NULLs if unmatched)")
print("# pandas how='right'  <-> SQL RIGHT JOIN   (all right rows, left NULLs if unmatched)")
print("# pandas how='outer'  <-> SQL FULL OUTER JOIN (union, NULLs on whichever side is missing)")
print("# pandas pd.concat(axis=0) <-> SQL UNION ALL (stack rows, keep duplicates)")
print("# See 02-DomainSpecificLanguage/SQL/03-Joins.sql for the same four modes in SQL.")

print("\n# End of Merging and Joining")
