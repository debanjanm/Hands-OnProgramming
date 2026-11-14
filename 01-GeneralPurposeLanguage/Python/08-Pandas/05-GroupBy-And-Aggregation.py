# 01. Split-Apply-Combine Mental Model
# 02. .groupby('col') then .sum()/.mean()/.count()
# 03. .agg() with Multiple Functions Per Column
# 04. .transform() - Same-Shape Result vs .agg()'s Collapse
# 05. Grouping by Multiple Columns
# 06. pd.pivot_table() as a GroupBy Convenience Wrapper

import pandas as pd
import numpy as np

sales = pd.DataFrame({
    "region": ["East", "East", "West", "West", "East", "West", "East", "West"],
    "product": ["Widget", "Gadget", "Widget", "Gadget", "Widget", "Widget", "Gadget", "Gadget"],
    "rep": ["Alice", "Alice", "Bob", "Carla", "Dev", "Bob", "Alice", "Carla"],
    "units": [10, 5, 8, 12, 20, 15, 7, 9],
    "revenue": [99.90, 122.50, 79.92, 294.00, 199.80, 149.85, 171.50, 220.50],
})
print("sales:\n", sales, sep="")

# 01. Split-Apply-Combine Mental Model
# ------------------------------------
# - SPLIT the DataFrame into groups based on some key (e.g. every unique
#   'region' value becomes its own group).
# - APPLY a function to each group independently (e.g. sum the 'revenue'
#   in each group).
# - COMBINE the per-group results back into a single Series/DataFrame,
#   indexed by the group keys.
# - .groupby() alone does nothing visible - it just builds the grouping
#   plan. The work happens when you call an aggregation like .sum() after it.

print("\n# 01. Split-Apply-Combine Mental Model")
print("# ------------------------------------")

grouped = sales.groupby("region")
print("sales.groupby('region') alone ->", grouped, "(a lazy GroupBy object, no output yet)")
print("Groups formed:", grouped.groups.keys())
print("# SPLIT: rows partitioned by region -> APPLY: e.g. sum -> COMBINE: one row per region")

# 02. .groupby('col') then .sum()/.mean()/.count()
# ------------------------------------
# - Calling an aggregation method after .groupby() runs it PER GROUP and
#   combines results, one output row per group, indexed by the group key.
# - Non-numeric columns are dropped automatically by numeric aggregations
#   like .sum()/.mean() (pandas 2.x requires numeric_only=True to be explicit
#   about it when other dtypes are present).

print("\n# 02. .groupby('col') then .sum()/.mean()/.count()")
print("# ------------------------------------")

print("sales.groupby('region')['revenue'].sum():\n", sales.groupby("region")["revenue"].sum(), sep="")
print("\nsales.groupby('region')['units'].mean():\n", sales.groupby("region")["units"].mean(), sep="")
print("\nsales.groupby('region').count() (counts non-null values per column, per group):")
print(sales.groupby("region").count())

# 03. .agg() with Multiple Functions Per Column
# ------------------------------------
# - .agg({'col1': 'func', 'col2': ['func1', 'func2']}) applies DIFFERENT
#   aggregation(s) to DIFFERENT columns in one call - far more flexible
#   than chaining separate .sum()/.mean() calls.

print("\n# 03. .agg() with Multiple Functions Per Column")
print("# ------------------------------------")

agg_result = sales.groupby("region").agg({"units": "sum", "revenue": ["sum", "mean", "max"]})
print("sales.groupby('region').agg({'units': 'sum', 'revenue': ['sum', 'mean', 'max']}):")
print(agg_result)

named_agg = sales.groupby("region").agg(
    total_units=("units", "sum"),
    avg_revenue=("revenue", "mean"),
)
print("\nNamed aggregation (clean flat column names) via agg(name=(col, func)):")
print(named_agg)

# 04. .transform() - Same-Shape Result vs .agg()'s Collapse
# ------------------------------------
# - .agg()/.sum()/.mean() COLLAPSE each group down to one summary row.
# - .transform() computes the same aggregation but BROADCASTS the result
#   back to the ORIGINAL shape/index - every row gets its group's value
#   attached, so it can be added straight back as a new column (no merge
#   needed to line group summaries back up with individual rows).

print("\n# 04. .transform() - Same-Shape Result vs .agg()'s Collapse")
print("# ------------------------------------")

region_avg_collapsed = sales.groupby("region")["revenue"].mean()
print(".mean() collapses to one row per region:\n", region_avg_collapsed, sep="")

region_avg_broadcast = sales.groupby("region")["revenue"].transform("mean")
print("\n.transform('mean') broadcasts back to all 8 original rows, aligned by index:")
print(region_avg_broadcast.tolist())

sales_with_avg = sales.copy()
sales_with_avg["region_avg_revenue"] = region_avg_broadcast
sales_with_avg["above_region_avg"] = sales_with_avg["revenue"] > sales_with_avg["region_avg_revenue"]
print("\nUsed directly as a new column (impossible with .agg()'s collapsed result without a merge):")
print(sales_with_avg[["region", "revenue", "region_avg_revenue", "above_region_avg"]])

# 05. Grouping by Multiple Columns
# ------------------------------------
# - groupby([col1, col2]) splits by every UNIQUE COMBINATION of the listed
#   columns, producing a MultiIndex result.

print("\n# 05. Grouping by Multiple Columns")
print("# ------------------------------------")

multi_group = sales.groupby(["region", "product"])["revenue"].sum()
print("sales.groupby(['region', 'product'])['revenue'].sum() (MultiIndex result):")
print(multi_group)
print("\nAccess one combination: multi_group.loc[('East', 'Widget')] =", multi_group.loc[("East", "Widget")])
print("reset_index() flattens the MultiIndex back into plain columns:")
print(multi_group.reset_index())

# 06. pd.pivot_table() as a GroupBy Convenience Wrapper
# ------------------------------------
# - pd.pivot_table(df, values=, index=, columns=, aggfunc=) is groupby +
#   reshape in one call: it groups by 'index' (and optionally 'columns' to
#   spread a second key across the columns axis), aggregates 'values', and
#   lays the result out as a wide table - equivalent to a groupby + unstack,
#   but usually more readable for a "region x product" summary table.

print("\n# 06. pd.pivot_table() as a GroupBy Convenience Wrapper")
print("# ------------------------------------")

pivot = pd.pivot_table(sales, values="revenue", index="region", columns="product", aggfunc="sum", fill_value=0)
print("pd.pivot_table(sales, values='revenue', index='region', columns='product', aggfunc='sum'):")
print(pivot)

print("\nEquivalent via groupby + unstack (pivot_table just does this for you):")
equivalent = sales.groupby(["region", "product"])["revenue"].sum().unstack(fill_value=0)
print(equivalent)
print("\nSame result:", pivot.equals(equivalent))

print("\n# End of GroupBy and Aggregation")
