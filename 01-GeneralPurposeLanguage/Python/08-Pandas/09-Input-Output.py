# 01. .to_csv() / pd.read_csv()
# 02. .to_json() / pd.read_json()
# 03. .to_excel() / pd.read_excel() (requires openpyxl - skips gracefully if missing)
# 04. Reading from a SQLite Database with pd.read_sql()
# 05. Cleanup

import pandas as pd
import sqlite3
import os

# Sample data used throughout - an orders table (ties in with the SQL folder's
# schema style: id, categorical column, date, numeric measure).
orders = pd.DataFrame({
    "order_id": [101, 102, 103, 104],
    "customer": ["Alice", "Bob", "Carla", "Dev"],
    "order_date": pd.to_datetime(["2024-01-05", "2024-01-12", "2024-02-01", "2024-02-15"]),
    "amount": [250.50, 89.99, 430.00, 15.75],
})
print("orders (source DataFrame used for every I/O example below):\n", orders)

# 01. .to_csv() / pd.read_csv()
# ------------------------------------
# - .to_csv(path, index=False) writes a DataFrame to disk. index=False skips
#   writing the row-index as its own column - without it, reloading the CSV
#   gives you a spurious 'Unnamed: 0' column.
# - pd.read_csv() key params:
#     dtype=       force a column's dtype on read (avoids pandas guessing wrong)
#     parse_dates= parse listed columns straight into datetime64
#     usecols=     load only the listed columns (saves memory on wide files)
#     na_values=   extra strings to treat as missing, beyond the built-in list

print("\n# 01. .to_csv() / pd.read_csv()")
print("# ------------------------------------")

orders.to_csv("temp_orders.csv", index=False)
print("Wrote temp_orders.csv with index=False")

with_index = pd.read_csv("temp_orders.csv")
print("\nread_csv with no extra params (order_date comes back as plain string/object):")
print(with_index.dtypes)

tuned = pd.read_csv(
    "temp_orders.csv",
    dtype={"order_id": "int32", "customer": "string"},
    parse_dates=["order_date"],
    usecols=["order_id", "customer", "order_date", "amount"],
    na_values=["N/A", "--"],
)
print("\nread_csv with dtype=/parse_dates=/usecols=/na_values= tuned:")
print(tuned.dtypes)
print(tuned)
print("# Without parse_dates, order_date reloads as a plain string ('object' dtype) -")
print("#   CSV has no type info, so pandas guesses, and dates are one of the things it gets wrong.")

# 02. .to_json() / pd.read_json()
# ------------------------------------
# - JSON preserves more type info than CSV (numbers stay numbers) but dates
#   still round-trip as strings or epoch millis unless handled explicitly.
# - orient='records' produces a list of {column: value} dicts - the most
#   common/portable layout for interchange with web APIs.

print("\n# 02. .to_json() / pd.read_json()")
print("# ------------------------------------")

orders.to_json("temp_orders.json", orient="records", date_format="iso")
print("Wrote temp_orders.json (orient='records', date_format='iso')")

with open("temp_orders.json") as f:
    print("Raw JSON (first 200 chars):", f.read()[:200])

reloaded_json = pd.read_json("temp_orders.json", orient="records")
print("\nReloaded from JSON:\n", reloaded_json)
print("dtypes:\n", reloaded_json.dtypes)

# 03. .to_excel() / pd.read_excel() (requires openpyxl - skips gracefully if missing)
# ------------------------------------
# - Excel I/O needs an extra engine library (openpyxl for .xlsx). Pandas
#   itself doesn't bundle it - check availability first so a script doesn't
#   crash on a machine where it's not installed.

print("\n# 03. .to_excel() / pd.read_excel() (requires openpyxl)")
print("# ------------------------------------")

try:
    import openpyxl  # noqa: F401  (presence check only)
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

if HAS_OPENPYXL:
    orders.to_excel("temp_orders.xlsx", index=False, sheet_name="orders")
    print("Wrote temp_orders.xlsx")
    reloaded_excel = pd.read_excel("temp_orders.xlsx", sheet_name="orders")
    print("Reloaded from Excel:\n", reloaded_excel)
else:
    print("openpyxl not installed - skipping .to_excel()/.read_excel() demo.")
    print("Install with: pip install openpyxl")

# 04. Reading from a SQLite Database with pd.read_sql()
# ------------------------------------
# - pd.read_sql(query, connection) runs a SQL query and returns the result
#   directly as a DataFrame - a natural bridge from the SQL folder in this
#   repo to pandas.
# - Uses an in-memory SQLite DB (":memory:") so no file is created; .to_sql()
#   writes a DataFrame INTO a table the same way read_sql reads one out.

print("\n# 04. Reading from a SQLite Database with pd.read_sql()")
print("# ------------------------------------")

conn = sqlite3.connect(":memory:")
orders.to_sql("orders", conn, index=False, if_exists="replace")
print("Loaded 'orders' DataFrame into an in-memory SQLite table via .to_sql()")

big_orders = pd.read_sql("SELECT customer, amount FROM orders WHERE amount > 100 ORDER BY amount DESC", conn)
print("\npd.read_sql() with a filtering/ordering query:\n", big_orders)
print("# Same SELECT ... WHERE ... ORDER BY syntax as 02-DomainSpecificLanguage/SQL/02-Filtering-And-Operators.sql -")
print("#   read_sql just routes the result straight into a DataFrame instead of a terminal table.")

conn.close()

# 05. Cleanup
# ------------------------------------
print("\n# 05. Cleanup")
for fname in ("temp_orders.csv", "temp_orders.json", "temp_orders.xlsx"):
    if os.path.exists(fname):
        os.remove(fname)
print("temp files removed")

print("\n# End of Input and Output")
