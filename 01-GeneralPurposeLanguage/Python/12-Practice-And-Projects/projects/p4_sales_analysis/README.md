# P4 - Sales Analysis Pipeline

Take messy sales data from raw tables to a finished report with charts, using **pandas** and **matplotlib**.
The data is made up by a seeded generator, so every run gives the same numbers.

## What you will practise
- spotting and fixing dirty data: duplicates, missing values, bad dates, outliers
- `groupby`, `merge`, `transform`, `unstack`, and `pd.to_datetime(errors="coerce")`
- cohort retention (a classic "do customers come back?" table)
- saving matplotlib charts to files with the `Agg` backend (no window needed)
- writing a small pipeline where each step is a plain function you can test
- testing DataFrames with `pandas.testing`

## Milestones
- [ ] 1. `generate.make_dataset(seed)` - customers, products, orders with deliberate dirt
- [ ] 2. `clean.py` - `clean_customers`, `clean_products`, `clean_orders`
- [ ] 3. `validate.py` - `validate` returns a list of problems, `assert_valid` raises
- [ ] 4. `features.add_features` - revenue, month, cohort columns
- [ ] 5. `kpis.py` - revenue by month and category, top customers, average order value
- [ ] 6. `kpis.cohort_retention`
- [ ] 7. `charts.py` - three PNG charts into a folder you are given
- [ ] 8. `report.py` - markdown tables and the report text
- [ ] 9. `report.run_pipeline(out_dir, seed)` ties everything together

## Public API (module.function)
| Function | Returns |
|---|---|
| `generate.make_dataset(seed=42, n_customers=120, n_orders=800)` | dict of raw DataFrames: `customers`, `products`, `orders` |
| `clean.clean_customers(df)`, `clean.clean_products(df)`, `clean.clean_orders(orders, products)` | cleaned DataFrames (fresh index) |
| `validate.validate(orders, customers, products)` | list of problem strings (empty = OK) |
| `validate.assert_valid(...)` | `None`, or raises `ValueError` |
| `features.add_features(orders, customers, products)` | one row per order, adds `revenue`, `order_month`, `first_month`, `cohort_index` |
| `kpis.revenue_by_month / revenue_by_category / top_customers / average_order_value / cohort_retention` | small DataFrames (or a float) |
| `charts.plot_*`, `charts.make_all(df, out_dir)` | `Path` / list of `Path` to the PNG files |
| `report.to_markdown_table`, `build_report`, `write_report`, `run_pipeline` | text / `Path` / dict |

Exact column names, sort orders and messages are in the docstrings of the starter files.

## Hints
- Set `os.environ.setdefault("MPLBACKEND", "Agg")` BEFORE `import matplotlib` (already done in `charts.py`).
- Parse dates with an explicit `format=` and `errors="coerce"`; bad ones become `NaT`.
- Always `.copy()` before changing a frame you were given.
- Look at `make_dataset()` output with `.info()` and `.describe()` before you clean it - find the dirt yourself.
- Work top to bottom: each step only needs the one before it.

## Run and test
From `12-Practice-And-Projects/`:
```
python3 -m pytest projects/p4_sales_analysis -q               # your code in starter/
python3 -m pytest projects/p4_sales_analysis -q --solutions   # the reference answer
cd projects/p4_sales_analysis/reference
python3 -c "from salesreport.report import run_pipeline; print(run_pipeline('out')['report'])"
```
(The last command writes an `out/` folder - delete it afterwards.)

## Stretch goals
- Add a customer lifetime value (CLV) table and a chart for it
- Detect outliers with the IQR rule instead of a fixed `MAX_QUANTITY`
- Add revenue by country and a "month over month growth %" column
- Write the report as HTML too
