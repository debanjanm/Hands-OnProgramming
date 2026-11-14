# 01. Wide vs Long Format - The Concept
# 02. .pivot() - Reshape Without Aggregation (Requires Unique Index/Column Pairs)
# 03. .pivot_table() - Reshape WITH Aggregation (Handles Duplicates)
# 04. .melt() - Wide to Long
# 05. .stack() / .unstack() - MultiIndex Reshaping
# 06. Full Round Trip - Wide -> Melt -> Pivot Back to Wide

import pandas as pd

# 01. Wide vs Long Format - The Concept
# ------------------------------------
# - WIDE format: one row per entity, each measured variable gets its OWN
#   COLUMN (e.g. one row per student, a column per subject). Easy to eyeball,
#   bad for filtering/grouping by "which variable".
# - LONG format: one row per (entity, variable, value) TRIPLE - every
#   measurement is its own row, with columns naming which variable it is.
#   Easy to filter/group/plot by variable, but repeats the entity's id.
# - This mental model matters more than the syntax: reshaping functions are
#   just converting between "variables as columns" and "variables as rows".

print("# 01. Wide vs Long Format - The Concept")
print("# ------------------------------------")

wide = pd.DataFrame({
    "student": ["Alice", "Bob", "Carla"],
    "math": [88, 72, 95],
    "science": [91, 68, 89],
    "art": [75, 90, 82],
})
print("WIDE format - one row per student, one column per subject:\n", wide)

long = wide.melt(id_vars="student", var_name="subject", value_name="score")
print("\nLONG format - one row per (student, subject) pair:\n", long)
print("# Same data, two shapes. Wide is for reading; long is for filtering/grouping")
print("#   ('give me every row where subject == math') and for most plotting libraries.")

# 02. .pivot() - Reshape Without Aggregation (Requires Unique Index/Column Pairs)
# ------------------------------------
# - .pivot(index=, columns=, values=) turns long data wide: index becomes
#   rows, columns become new column headers, values fills the cells.
# - It does NOT aggregate - if a given (index, columns) combination appears
#   MORE THAN ONCE, pivot cannot decide which value to keep and raises.

print("\n# 02. .pivot() - Reshape Without Aggregation")
print("# ------------------------------------")

clean_long = pd.DataFrame({
    "student": ["Alice", "Alice", "Bob", "Bob"],
    "subject": ["math", "science", "math", "science"],
    "score": [88, 91, 72, 68],
})
print("clean_long (each student/subject pair appears once):\n", clean_long)

pivoted = clean_long.pivot(index="student", columns="subject", values="score")
print("\n.pivot(index='student', columns='subject', values='score'):\n", pivoted)

# Now break the uniqueness assumption: Alice has TWO math scores (retake).
dup_long = pd.DataFrame({
    "student": ["Alice", "Alice", "Bob"],
    "subject": ["math", "math", "science"],
    "score": [88, 95, 68],
})
print("\ndup_long (Alice has two 'math' rows - a retake):\n", dup_long)
try:
    dup_long.pivot(index="student", columns="subject", values="score")
except ValueError as e:
    print(".pivot() raises ValueError:", e)
print("# pivot() needs each (index, columns) pair to be unique. Duplicates -> use pivot_table().")

# 03. .pivot_table() - Reshape WITH Aggregation (Handles Duplicates)
# ------------------------------------
# - Same idea as pivot(), but when multiple rows share an (index, columns)
#   pair, it AGGREGATES them with aggfunc (default 'mean') instead of erroring.
# - Recap from the groupby file: pivot_table is essentially groupby(index +
#   columns) followed by a reshape into a grid.

print("\n# 03. .pivot_table() - Reshape WITH Aggregation")
print("# ------------------------------------")

pt_mean = dup_long.pivot_table(index="student", columns="subject", values="score", aggfunc="mean")
print("dup_long.pivot_table(..., aggfunc='mean') averages Alice's two math scores:\n", pt_mean)

pt_max = dup_long.pivot_table(index="student", columns="subject", values="score", aggfunc="max")
print("\nSame data, aggfunc='max' (keeps the retake's better score):\n", pt_max)
print("# Rule of thumb: know your (index, columns) pairs are unique -> pivot() (fails loudly on")
print("#   a violated assumption). Might have duplicates -> pivot_table() (aggregates them).")

# 04. .melt() - Wide to Long
# ------------------------------------
# - .melt(id_vars=, value_vars=) is the inverse of pivot: collapses several
#   columns into two - one naming which column each value came from ('variable',
#   overridable via var_name), one holding the value itself (value_name).
# - id_vars = columns to KEEP as-is (identifiers); value_vars = columns to
#   unpivot (defaults to "every column not in id_vars").

print("\n# 04. .melt() - Wide to Long")
print("# ------------------------------------")

quarterly = pd.DataFrame({
    "region": ["East", "West"],
    "q1_sales": [50000, 42000],
    "q2_sales": [55000, 47000],
    "q3_sales": [60000, 45000],
})
print("quarterly (wide, one column per quarter):\n", quarterly)

melted = quarterly.melt(id_vars="region", value_vars=["q1_sales", "q2_sales", "q3_sales"],
                         var_name="quarter", value_name="sales")
print("\nmelted (long, one row per region/quarter):\n", melted)
print("# value_vars is optional here since it covers every non-id_vars column anyway -")
print("#   pass it explicitly when you only want to melt a SUBSET of columns.")

# 05. .stack() / .unstack() - MultiIndex Reshaping
# ------------------------------------
# - .stack() pivots COLUMNS into an inner level of the ROW index (wide -> long,
#   operating on the index instead of named id_vars/value_vars).
# - .unstack() is the inverse: pivots an inner ROW index level out into columns.
# - Both operate on MultiIndex structure directly - the "columns" and "index
#   levels" ARE the reshaping mechanism, no column-name arguments needed.

print("\n# 05. .stack() / .unstack() - MultiIndex Reshaping")
print("# ------------------------------------")

multi_wide = pd.DataFrame(
    {"math": [88, 72], "science": [91, 68]},
    index=pd.Index(["Alice", "Bob"], name="student"),
)
print("multi_wide:\n", multi_wide)

stacked = multi_wide.stack()
print("\n.stack() moves 'subject' from columns into an inner index level:\n", stacked)
print("Result type:", type(stacked).__name__, "- a Series with a 2-level MultiIndex", stacked.index.names)

unstacked_back = stacked.unstack()
print("\n.unstack() moves it back out into columns (round trip):\n", unstacked_back)
print("Equal to original:", unstacked_back.equals(multi_wide))

# 06. Full Round Trip - Wide -> Melt -> Pivot Back to Wide
# ------------------------------------
# - Cements the relationship: melt() and pivot() are inverses of each other,
#   provided nothing was aggregated away in between.

print("\n# 06. Full Round Trip - Wide -> Melt -> Pivot Back to Wide")
print("# ------------------------------------")

original_wide = pd.DataFrame({
    "student": ["Alice", "Bob", "Carla"],
    "math": [88, 72, 95],
    "science": [91, 68, 89],
})
print("Step 1 - original_wide:\n", original_wide)

step2_long = original_wide.melt(id_vars="student", var_name="subject", value_name="score")
print("\nStep 2 - melt() to long:\n", step2_long)

step3_wide_again = step2_long.pivot(index="student", columns="subject", values="score")
step3_wide_again = step3_wide_again.reset_index()
step3_wide_again.columns.name = None  # cosmetic: drop the leftover 'subject' columns-axis name
print("\nStep 3 - pivot() back to wide (reset_index to restore 'student' as a column):\n", step3_wide_again)

# Reorder columns to match the original before comparing (pivot alphabetizes columns).
step3_reordered = step3_wide_again[original_wide.columns]
print("\nRound trip recovers the original data:", step3_reordered.equals(original_wide))

print("\n# End of Reshaping")
