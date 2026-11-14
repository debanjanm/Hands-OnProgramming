# 01. Creating a Series
# 02. Creating a DataFrame
# 03. Core Attributes (.shape, .columns, .index, .values, .dtypes)
# 04. .info() and .describe()
# 05. .head() / .tail()
# 06. Series <-> DataFrame Relationship

import pandas as pd
import numpy as np

# 01. Creating a Series
# ------------------------------------
# - A Series is a 1D labeled array: values + an index (like a single column
#   with row labels attached).
# - Build it from a list (gets a default RangeIndex 0..n-1), from a dict
#   (keys become the index), or with an explicit custom index.

print("# 01. Creating a Series")
print("# ------------------------------------")

s_from_list = pd.Series([100, 200, 300, 400])
print("From list (default RangeIndex):\n", s_from_list, sep="")

s_from_dict = pd.Series({"apples": 50, "bananas": 30, "cherries": 90})
print("\nFrom dict (dict keys become the index):\n", s_from_dict, sep="")

s_custom_index = pd.Series([10.5, 20.1, 15.75], index=["Mon", "Tue", "Wed"])
print("\nWith custom index:\n", s_custom_index, sep="")
print("\nName + dtype are part of the Series:", s_custom_index.name, s_custom_index.dtype)
print("Access by label:", s_custom_index["Tue"], "| Access by position:", s_custom_index.iloc[1])

# 02. Creating a DataFrame
# ------------------------------------
# - A DataFrame is a 2D labeled table: rows + columns, each column is a Series.
# - Common construction paths: dict of lists (keys -> column names), list of
#   dicts (each dict -> one row), or a raw NumPy array with columns=/index=
#   supplied separately since an ndarray has no labels of its own.

print("\n# 02. Creating a DataFrame")
print("# ------------------------------------")

employees = pd.DataFrame({
    "name": ["Alice", "Bob", "Carla", "Dev"],
    "department": ["Engineering", "Sales", "Engineering", "Marketing"],
    "salary": [95000, 62000, 88000, 71000],
    "years": [3, 7, 2, 5],
})
print("From dict of lists (dict keys -> column names):\n", employees, sep="")

rows = [
    {"name": "Alice", "salary": 95000},
    {"name": "Bob", "salary": 62000},
]
print("\nFrom list of dicts (each dict -> one row, missing keys become NaN):\n", pd.DataFrame(rows), sep="")

arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
df_from_array = pd.DataFrame(arr, columns=["x", "y", "z"], index=["r1", "r2", "r3"])
print("\nFrom a NumPy array (array has no labels, so pass columns=/index= explicitly):")
print(df_from_array)

# 03. Core Attributes
# ------------------------------------
# - .shape        -> (n_rows, n_cols), same convention as NumPy.
# - .columns      -> an Index object holding column labels.
# - .index        -> an Index object holding row labels.
# - .values       -> the underlying data as a NumPy array (drops labels;
#                    if columns have mixed dtypes the result upcasts to
#                    a common dtype, usually object).
# - .dtypes       -> per-column dtype (a Series indexed by column name) -
#                    unlike NumPy, EACH COLUMN can have its own dtype.

print("\n# 03. Core Attributes")
print("# ------------------------------------")

print("employees.shape   =", employees.shape)
print("employees.columns =", list(employees.columns))
print("employees.index   =", list(employees.index))
print("employees.dtypes:\n", employees.dtypes, sep="")
print("\nemployees.values (mixed dtypes -> upcasts to object array):\n", employees.values)

# 04. .info() and .describe()
# ------------------------------------
# - .info() prints structure: dtypes, non-null counts per column, memory
#   usage - the first thing to run on an unfamiliar DataFrame to spot
#   missing values and wrong dtypes at a glance.
# - .describe() gives summary stats for numeric columns by default
#   (count/mean/std/min/quartiles/max); pass include='all' to also summarize
#   object/categorical columns (count/unique/top/freq).

print("\n# 04. .info() and .describe()")
print("# ------------------------------------")

print("employees.info():")
employees.info()

print("\nemployees.describe() (numeric columns only by default):")
print(employees.describe())

print("\nemployees.describe(include='all') (adds unique/top/freq for object columns):")
print(employees.describe(include="all"))

# 05. .head() / .tail()
# ------------------------------------
# - .head(n) / .tail(n) return the first/last n rows (default n=5) - the
#   standard "quick peek" for a DataFrame too large to print in full.

print("\n# 05. .head() / .tail()")
print("# ------------------------------------")

print("employees.head(2):\n", employees.head(2), sep="")
print("\nemployees.tail(2):\n", employees.tail(2), sep="")

# 06. Series <-> DataFrame Relationship
# ------------------------------------
# - A DataFrame behaves like a dict-like collection of Series that all
#   share the same row index. Pulling out one column with df['col'] gives
#   back a Series - not a copy of unrelated data, but a labeled view aligned
#   to the same index as the DataFrame it came from.

print("\n# 06. Series <-> DataFrame Relationship")
print("# ------------------------------------")

salary_col = employees["salary"]
print("type(employees['salary']) =", type(salary_col))
print("salary_col shares employees' index:", list(salary_col.index) == list(employees.index))
print("salary_col:\n", salary_col, sep="")
print("\n# A DataFrame is essentially {col_name: Series, ...} where every Series")
print("#   shares one common index - that's why df['salary'] + df['years'] aligns")
print("#   by row automatically instead of needing manual position matching.")

print("\n# End of Series and DataFrame Basics")
