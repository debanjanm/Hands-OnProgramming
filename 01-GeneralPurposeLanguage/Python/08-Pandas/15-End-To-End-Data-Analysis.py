# 01. The Workflow Map
# 02. Build Messy Synthetic Data (customers, products, orders)
# 03. Load and Inspect
# 04. Clean: Text, Types, Dates (documented decisions)
# 05. Clean: Duplicates, Invalid Values, Missing Values
# 06. Validate with Assertions
# 07. Merge the Three Tables Safely
# 08. Feature Engineering
# 09. KPIs: Revenue, Orders, Average Order Value
# 10. Top-N Analysis
# 11. Cohort Retention Table with pivot_table
# 12. Rolling Trends
# 13. Outliers: IQR and z-score
# 14. A Method-Chained Pipeline with pipe
# 15. A Data-Quality Checklist Function
# 16. Save Results and Read Them Back
# 17. Final Summary
# 18. Anti-pattern 1: iterrows
# 19. Anti-pattern 2: Chained Assignment
# 20. Anti-pattern 3: concat Inside a Loop
# 21. Anti-pattern 4: apply for Something Vectorizable
#
# Related: 03-Data-Cleaning, 05-GroupBy-And-Aggregation, 06-Merging-And-Joining,
# 07-Reshaping, 08-Time-Series, 09-Input-Output, 10-Performance-And-Best-Practices.
# This file shows how those pieces fit together in one realistic workflow.

import os
import tempfile
import numpy as np
import pandas as pd

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)

# 01. The Workflow Map
# ----------------------------
# - A real analysis is not "one clever groupby". It is a repeatable chain:
#   load -> inspect -> clean -> validate -> enrich -> analyse -> save -> report.
# - Each cleaning step is a DECISION (drop? fill? flag?). Write the decision and
#   the reason next to the code. Future you will thank you.
# - Validate with assert right after cleaning: if the data breaks your
#   assumptions, you want a loud crash, not a quietly wrong report.
# - Keep the RAW data untouched (copy before changing). Re-runnable beats clever.

print("Workflow: load -> inspect -> clean -> validate -> enrich -> analyse -> save -> report")

# 02. Build Messy Synthetic Data (customers, products, orders)
# ----------------------------
# - Fully seeded (default_rng(42)): same data every run, no files needed.
# - The mess is added ON PURPOSE so each cleaning step has something to fix:
#   dirty region text, string dates with garbage, duplicate rows, invalid
#   quantities, missing discounts, orphan customer ids, a few giant orders.

rng = np.random.default_rng(42)

n_cust = 200
regions = np.array(["North", "South", "East", "West"])
raw_customers = pd.DataFrame({
    "customer_id": np.arange(1, n_cust + 1),
    "region": rng.choice(regions, n_cust),
    "signup_date": (pd.Timestamp("2022-06-01") + pd.to_timedelta(rng.integers(0, 200, n_cust), unit="D")).strftime("%Y-%m-%d"),
})
# dirty: stray spaces and inconsistent case in a few regions
raw_customers.loc[[3, 10, 25, 60], "region"] = [" north", "SOUTH ", "east", "West  "]

raw_products = pd.DataFrame({
    "product_id": np.arange(1, 13),
    "category": ["Toys", "Toys", "Toys", "Books", "Books", "Books",
                 "Garden", "Garden", "Garden", "Tech", "Tech", "Tech"],
    "unit_price": [12.5, 20.0, 35.0, 9.0, 15.0, 25.0, 18.0, 40.0, 60.0, 80.0, 150.0, 300.0],
})

n_orders = 1500
days = rng.integers(0, 365, n_orders)
raw_orders = pd.DataFrame({
    "order_id": np.arange(1, n_orders + 1),
    "customer_id": rng.integers(1, n_cust + 1, n_orders),
    "product_id": rng.integers(1, 13, n_orders),
    "quantity": rng.integers(1, 5, n_orders),
    "order_date": (pd.Timestamp("2023-01-01") + pd.to_timedelta(days, unit="D")).strftime("%Y-%m-%d"),
    "discount_pct": rng.choice([0.0, 5.0, 10.0, 20.0], n_orders),
})
# --- inject mess (deterministic positions) ---
raw_orders.loc[[5, 77, 400], "quantity"] = [0, -2, -1]            # invalid quantities
raw_orders.loc[[9, 120, 800, 801], "order_date"] = ["n/a", "2023-13-45", "not a date", "2023-02-30"]
raw_orders.loc[rng.choice(n_orders, 90, replace=False), "discount_pct"] = np.nan
raw_orders.loc[[15, 16, 17], "customer_id"] = 999                 # orphans: not in customers
raw_orders.loc[[200, 900, 1300], "quantity"] = [60, 80, 70]       # giant (maybe bulk) orders
raw_orders = pd.concat([raw_orders, raw_orders.iloc[[1, 2, 3, 40, 41]]], ignore_index=True)  # exact duplicates

print("raw customers:", raw_customers.shape, "| raw products:", raw_products.shape, "| raw orders:", raw_orders.shape)

# 03. Load and Inspect
# ----------------------------
# - Always look BEFORE you touch: shape, dtypes, head, missing counts, describe.
# - dtypes tell you what went wrong at load: dates are still object (text).
# - describe() on numbers: look at min/max for impossible values.
# - value_counts() on text columns exposes inconsistent spellings.

print("\norders head:\n", raw_orders.head(), sep="")
print("\norders dtypes:\n", raw_orders.dtypes, sep="")
print("\nmissing values per column:\n", raw_orders.isna().sum(), sep="")
print("\nnumeric describe:\n", raw_orders[["quantity", "discount_pct"]].describe().round(2), sep="")
print("\ncustomer region spellings:\n", raw_customers["region"].value_counts().sort_index(), sep="")
print("\nduplicate rows in orders:", int(raw_orders.duplicated().sum()))

# 04. Clean: Text, Types, Dates (documented decisions)
# ----------------------------
# - DECISION 1: region text is trimmed + title-cased. Reason: " north" and
#   "North" are the same region; otherwise groupby splits them.
# - DECISION 2: dates parsed with an explicit format and errors='coerce'.
#   Bad dates become NaT and are COUNTED, then dropped (an order with no date
#   cannot be placed in time, so it cannot be used in trends or cohorts).
# - DECISION 3: ids stay int; categories become 'category' dtype (less memory,
#   typo-proof).
# - Work on COPIES so raw_* stay as the untouched source of truth.

customers = raw_customers.copy()
customers["region"] = customers["region"].str.strip().str.title()
customers["signup_date"] = pd.to_datetime(customers["signup_date"], format="%Y-%m-%d")
customers["region"] = customers["region"].astype("category")
print("regions after cleaning:", customers["region"].value_counts().sort_index().to_dict())

products = raw_products.copy()
products["category"] = products["category"].astype("category")

orders = raw_orders.copy()
orders["order_date"] = pd.to_datetime(orders["order_date"], format="%Y-%m-%d", errors="coerce")
bad_dates = int(orders["order_date"].isna().sum())
print("unparseable dates (coerced to NaT):", bad_dates)
print("those raw values:", raw_orders.loc[orders["order_date"].isna(), "order_date"].tolist())

# 05. Clean: Duplicates, Invalid Values, Missing Values
# ----------------------------
# - DECISION 4: exact duplicate rows are dropped (same order_id twice is a
#   double-load, not two sales). Check on order_id first, then drop.
# - DECISION 5: quantity <= 0 is invalid. Dropped, not "fixed" - we do not
#   know the true value, and returns would belong in a separate table.
# - DECISION 6: missing discount means "no discount recorded" -> fill with 0
#   AND keep a flag column, so the fill is visible later, not hidden.
# - DECISION 7: rows with NaT date are dropped (see section 04).
# - Print row counts at every step - a cleaning log you can audit.

log = [("raw", len(orders))]
orders = orders.drop_duplicates()
log.append(("drop exact duplicates", len(orders)))
orders = orders.dropna(subset=["order_date"])
log.append(("drop missing/bad dates", len(orders)))
orders = orders[orders["quantity"] > 0].copy()          # .copy() avoids SettingWithCopy later
log.append(("drop quantity <= 0", len(orders)))
orders["discount_missing"] = orders["discount_pct"].isna()
orders["discount_pct"] = orders["discount_pct"].fillna(0.0)
orders = orders.reset_index(drop=True)
for step, n in log:
    print(f"  {step:<26} -> {n} rows")
print("discount filled with 0 on", int(orders["discount_missing"].sum()), "rows (flagged in discount_missing)")

# 06. Validate with Assertions
# ----------------------------
# - assert statements turn assumptions into checks. If one fails the script
#   stops with a message - better than a wrong KPI in a report.
# - Check: key uniqueness, no nulls in critical columns, value ranges, date range.
# - Orphan foreign keys (orders pointing to missing customers) are checked
#   separately because they are a finding to REPORT, not always a crash.

assert orders["order_id"].is_unique, "order_id must be unique"
assert orders[["customer_id", "product_id", "order_date", "quantity"]].notna().all().all(), "critical nulls"
assert (orders["quantity"] > 0).all(), "quantity must be positive"
assert orders["discount_pct"].between(0, 100).all(), "discount out of range"
assert orders["order_date"].between("2023-01-01", "2023-12-31").all(), "date outside expected year"
assert customers["customer_id"].is_unique and products["product_id"].is_unique
assert set(orders["product_id"]) <= set(products["product_id"]), "unknown product ids"
print("all hard assertions passed")

orphans = ~orders["customer_id"].isin(customers["customer_id"])
print("orders pointing to unknown customers:", int(orphans.sum()), "(customer ids:", sorted(orders.loc[orphans, "customer_id"].unique().tolist()), ")")
print("DECISION 8: keep orphans out of customer-level analysis, but keep them in a quarantine table")
quarantine = orders[orphans]
orders = orders[~orphans].reset_index(drop=True)
print("quarantined rows:", len(quarantine), "| clean orders left:", len(orders))

# 07. Merge the Three Tables Safely
# ----------------------------
# - how='left' keeps every order; validate='m:1' makes pandas raise if the
#   right table has duplicate keys (which would silently multiply rows).
# - indicator=True shows which rows matched; assert none are 'left_only'.
# - Assert the row count did not change: a merge that changes the number of
#   orders is a bug, not a result.

before = len(orders)
df = (orders
      .merge(customers, on="customer_id", how="left", validate="m:1", indicator="cust_match")
      .merge(products, on="product_id", how="left", validate="m:1"))
assert len(df) == before, "merge changed the row count!"
assert (df["cust_match"] == "both").all()
df = df.drop(columns="cust_match")
print("merged:", df.shape)
print(df.head(3))

# 08. Feature Engineering
# ----------------------------
# - Gross revenue = quantity * unit_price; net applies the discount.
# - Date parts via .dt: month period, weekday name, weekend flag.
# - Customer-level features via groupby().transform (broadcast back to rows).
# - Use vectorized math and np.select/np.where, not row loops.
# - pd.cut for a business-friendly size bucket (labels are your documentation).

df["gross"] = df["quantity"] * df["unit_price"]
df["net"] = (df["gross"] * (1 - df["discount_pct"] / 100)).round(2)
df["month"] = df["order_date"].dt.to_period("M")
df["weekday"] = df["order_date"].dt.day_name()
df["is_weekend"] = df["order_date"].dt.dayofweek >= 5
df["first_order"] = df.groupby("customer_id")["order_date"].transform("min")
df["days_since_signup"] = (df["order_date"] - df["signup_date"]).dt.days
df["size"] = pd.cut(df["net"], bins=[0, 50, 200, 1000, np.inf], labels=["small", "medium", "large", "xl"])
df["is_new_customer_order"] = df["order_date"].eq(df["first_order"])
print(df[["order_id", "net", "month", "weekday", "size", "days_since_signup"]].head())
print("size bucket counts:", df["size"].value_counts(sort=False).to_dict())
print("total net revenue:", round(df["net"].sum(), 2))

# 09. KPIs: Revenue, Orders, Average Order Value
# ----------------------------
# - Named aggregation (agg(name=(col, func))) gives clean, readable KPI tables.
# - nunique for distinct customers; AOV = revenue / orders (compute AFTER
#   aggregating, do not average the averages).
# - Share of total with .div(total) shows who matters.
# - observed=True with categorical keys avoids empty groups (and a warning).

by_month = df.groupby("month").agg(
    orders=("order_id", "count"),
    customers=("customer_id", "nunique"),
    revenue=("net", "sum"),
).assign(aov=lambda t: (t["revenue"] / t["orders"]).round(2))
by_month["revenue"] = by_month["revenue"].round(2)
print("monthly KPIs (first 6 months):\n", by_month.head(6), sep="")

by_cat = df.groupby("category", observed=True).agg(revenue=("net", "sum"), units=("quantity", "sum"))
by_cat["share_pct"] = (by_cat["revenue"] / by_cat["revenue"].sum() * 100).round(1)
print("\nby category:\n", by_cat.round(2).sort_values("revenue", ascending=False), sep="")
by_region = df.groupby("region", observed=True)["net"].agg(["sum", "mean"]).round(2)
print("\nby region:\n", by_region, sep="")

# 10. Top-N Analysis
# ----------------------------
# - nlargest / nsmallest on an aggregated Series is the shortest top-N.
# - Top-N PER GROUP: sort then groupby().head(n), or groupby + nlargest.
# - Add tie-breaking (a second sort key) so results are deterministic.

top_customers = df.groupby("customer_id")["net"].sum().round(2).nlargest(5)
print("top 5 customers by revenue:\n", top_customers, sep="")
prod_rev = df.groupby(["category", "product_id"], observed=True)["net"].sum().round(2).reset_index()
top2_per_cat = (prod_rev.sort_values(["category", "net", "product_id"], ascending=[True, False, True])
                .groupby("category", observed=True).head(2))
print("\ntop 2 products inside each category:\n", top2_per_cat.to_string(index=False), sep="")
print("\ncustomers needed for 50% of revenue:",
      int((df.groupby("customer_id")["net"].sum().sort_values(ascending=False).cumsum()
           / df["net"].sum() < 0.5).sum()) + 1, "of", df["customer_id"].nunique())

# 11. Cohort Retention Table with pivot_table
# ----------------------------
# - Cohort = the month of a customer's FIRST order.
# - cohort_index = whole months since that first month (0 = the cohort month).
# - pivot_table(index=cohort, columns=cohort_index, values=customer_id,
#   aggfunc='nunique') counts distinct active customers.
# - Retention % = each cell divided by the month-0 column of its row.
# - Do month math with year*12+month: vectorized, no apply needed.

df["cohort"] = df.groupby("customer_id")["month"].transform("min")
df["cohort_index"] = ((df["month"].dt.year - df["cohort"].dt.year) * 12
                      + (df["month"].dt.month - df["cohort"].dt.month))
cohort_counts = df.pivot_table(index="cohort", columns="cohort_index", values="customer_id", aggfunc="nunique")
retention = cohort_counts.div(cohort_counts[0], axis=0).mul(100).round(0)
print("active customers by cohort (first 5 cohorts, first 6 months):\n", cohort_counts.iloc[:5, :6].fillna(0).astype(int), sep="")
print("\nretention % (first 5 cohorts, first 6 months):\n", retention.iloc[:5, :6], sep="")
print("\nnote: later cohorts have fewer columns - they have not existed long enough (NaN, not 0)")

# 12. Rolling Trends
# ----------------------------
# - Resample to a regular daily series first (gaps filled with 0 revenue),
#   THEN roll. Rolling over irregular rows mixes "last 7 rows" with "last 7 days".
# - rolling(7).mean() -> first 6 values are NaN unless min_periods is set.
# - Compare against the previous period with .pct_change() on the monthly total.
# - expanding().sum() gives running (year-to-date) totals.

daily = df.set_index("order_date")["net"].resample("D").sum()
roll7 = daily.rolling(7).mean()
print("daily series length:", len(daily), "| first 6 rolling values are NaN:", int(roll7.isna().sum()))
print("last 3 days: revenue and 7-day mean:\n",
      pd.DataFrame({"revenue": daily, "roll7": roll7.round(1)}).tail(3), sep="")
monthly = df.groupby("month")["net"].sum()
print("\nmonth-over-month growth % (first 5):", (monthly.pct_change() * 100).round(1).head(5).tolist())
print("rolling 3-month revenue (last 3):", monthly.rolling(3).sum().round(0).tail(3).tolist())
print("year-to-date revenue at year end:", round(monthly.expanding().sum().iloc[-1], 2))
print("busiest weekday by revenue:", df.groupby("weekday")["net"].sum().idxmax())

# 13. Outliers: IQR and z-score
# ----------------------------
# - IQR rule: outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR]. Robust, does not assume a
#   bell curve; good for skewed money data.
# - z-score: (x - mean) / std. Simple, but the outlier itself inflates mean and
#   std, so extreme values can hide themselves. Use |z| > 3 as a rough rule.
# - Detecting is not deleting. DECISION 9: FLAG outliers; keep them in totals
#   but report revenue with and without them.

q1, q3 = df["net"].quantile([0.25, 0.75])
iqr = q3 - q1
low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
df["out_iqr"] = ~df["net"].between(low, high)
z = (df["net"] - df["net"].mean()) / df["net"].std()
df["out_z"] = z.abs() > 3
print(f"IQR fences: [{low:.1f}, {high:.1f}] | flagged by IQR: {int(df['out_iqr'].sum())} | flagged by |z|>3: {int(df['out_z'].sum())}")
print("flagged by z are a subset of IQR flags:", bool((df["out_z"] <= df["out_iqr"]).all()))
print("giant quantity orders:\n", df.loc[df["quantity"] >= 60, ["order_id", "quantity", "net", "out_iqr", "out_z"]], sep="")
print("revenue incl. outliers:", round(df["net"].sum(), 2), "| excl. z-outliers:", round(df.loc[~df["out_z"], "net"].sum(), 2))
per_cat = df.groupby("category", observed=True)["net"].transform(lambda s: (s - s.mean()) / s.std())
print("outliers per category use a group-wise z (|z|>3):", int((per_cat.abs() > 3).sum()))

# 14. A Method-Chained Pipeline with pipe
# ----------------------------
# - Wrap each stage in a small function that takes a DataFrame and RETURNS a
#   new one. Then df.pipe(f1).pipe(f2) reads like a recipe.
# - Each function copies / assigns instead of mutating the caller's data, so
#   the pipeline is safe to re-run and easy to test one step at a time.
# - pipe(f, arg=...) forwards extra arguments.
# - Proof of correctness: the pipeline on RAW data must equal what we built
#   step by step above.

def clean_orders(o: pd.DataFrame) -> pd.DataFrame:
    return (o.assign(order_date=lambda t: pd.to_datetime(t["order_date"], format="%Y-%m-%d", errors="coerce"))
             .drop_duplicates()
             .dropna(subset=["order_date"])
             .query("quantity > 0")
             .assign(discount_missing=lambda t: t["discount_pct"].isna(),
                     discount_pct=lambda t: t["discount_pct"].fillna(0.0))
             .reset_index(drop=True))

def drop_orphans(o: pd.DataFrame, cust: pd.DataFrame) -> pd.DataFrame:
    return o[o["customer_id"].isin(cust["customer_id"])].reset_index(drop=True)

def enrich(o: pd.DataFrame, cust: pd.DataFrame, prod: pd.DataFrame) -> pd.DataFrame:
    return (o.merge(cust, on="customer_id", how="left", validate="m:1")
             .merge(prod, on="product_id", how="left", validate="m:1")
             .assign(gross=lambda t: t["quantity"] * t["unit_price"],
                     net=lambda t: (t["quantity"] * t["unit_price"] * (1 - t["discount_pct"] / 100)).round(2)))

pipeline_df = (raw_orders
               .pipe(clean_orders)
               .pipe(drop_orphans, cust=customers)
               .pipe(enrich, cust=customers, prod=products))
print("pipeline result shape:", pipeline_df.shape)
print("same rows and net revenue as the step-by-step build:",
      len(pipeline_df) == len(df), pipeline_df["net"].equals(df["net"]))
print("input untouched by the pipeline (raw still has", len(raw_orders), "rows with", int(raw_orders.duplicated().sum()), "duplicates)")

# 15. A Data-Quality Checklist Function
# ----------------------------
# - Wrap checks in one function that returns a small report DataFrame
#   (check name, passed?, detail). Run it before AND after cleaning to show
#   the improvement, and run it on every new data drop.
# - Checks here: row count, key uniqueness, nulls, duplicates, negatives,
#   date parse failures, referential integrity.

def data_quality_report(o: pd.DataFrame, cust: pd.DataFrame) -> pd.DataFrame:
    dates = pd.to_datetime(o["order_date"], format="%Y-%m-%d", errors="coerce")
    checks = {
        "order_id unique": (o["order_id"].is_unique, f"{int(o['order_id'].duplicated().sum())} repeats"),
        "no duplicate rows": (not o.duplicated().any(), f"{int(o.duplicated().sum())} dup rows"),
        "dates parse": (dates.notna().all(), f"{int(dates.isna().sum())} bad dates"),
        "quantity positive": ((o["quantity"] > 0).all(), f"{int((o['quantity'] <= 0).sum())} non-positive"),
        "discount present": (o["discount_pct"].notna().all(), f"{int(o['discount_pct'].isna().sum())} missing"),
        "customers exist": (o["customer_id"].isin(cust["customer_id"]).all(),
                            f"{int((~o['customer_id'].isin(cust['customer_id'])).sum())} orphans"),
    }
    return pd.DataFrame([(k, "PASS" if ok else "FAIL", d) for k, (ok, d) in checks.items()],
                        columns=["check", "status", "detail"])

print("quality report on RAW orders:\n", data_quality_report(raw_orders, raw_customers).to_string(index=False), sep="")
cleaned = raw_orders.pipe(clean_orders).pipe(drop_orphans, cust=customers)
print("\nquality report on CLEANED orders:\n", data_quality_report(cleaned, customers).to_string(index=False), sep="")

# 16. Save Results and Read Them Back
# ----------------------------
# - Write outputs somewhere disposable: tempfile.TemporaryDirectory() deletes
#   everything on exit, so no leftover files.
# - CSV: universal but loses dtypes (dates come back as text, categories as
#   object). Pass parse_dates=/dtype= on read, and index=False on write.
# - Parquet: keeps dtypes, smaller, faster. Needs pyarrow or fastparquet, so
#   guard the call with try/except ImportError.
# - Always read back and compare: a save you never verified is a hope.
# - Cross-reference: 09-Input-Output covers the full IO options.

summary_table = by_month.reset_index()
summary_table["month"] = summary_table["month"].astype(str)   # Period dtype does not round-trip through CSV
with tempfile.TemporaryDirectory() as tmp:
    csv_path = os.path.join(tmp, "monthly_kpis.csv")
    summary_table.to_csv(csv_path, index=False)
    back = pd.read_csv(csv_path)
    print("CSV round trip equal:", back.equals(summary_table), "| dtypes kept:", back.dtypes.equals(summary_table.dtypes))
    print("CSV file is under 2000 bytes:", os.path.getsize(csv_path) < 2000)
    try:
        pq_path = os.path.join(tmp, "orders_clean.parquet")
        out = df[["order_id", "customer_id", "order_date", "net", "category"]]
        out.to_parquet(pq_path, index=False)
        back_pq = pd.read_parquet(pq_path)
        print("Parquet round trip equal:", back_pq.equals(out), "| category dtype survives:", back_pq["category"].dtype)
    except ImportError:
        print("parquet engine not installed - skipping (pip install pyarrow)")
    print("files in temp dir while open:", sorted(os.listdir(tmp)))
print("temp dir removed after the with block:", not os.path.exists(tmp))

# 17. Final Summary
# ----------------------------
# - End every analysis with a short, human summary: scope, headline numbers,
#   caveats. The numbers come from variables, never typed by hand.

best_month = monthly.idxmax()
print("=" * 50)
print("ANALYSIS SUMMARY")
print("=" * 50)
print(f"raw order rows        : {len(raw_orders)}")
print(f"clean order rows      : {len(df)} (+{len(quarantine)} quarantined orphans)")
print(f"customers active      : {df['customer_id'].nunique()}")
print(f"total net revenue     : {df['net'].sum():,.2f}")
print(f"average order value   : {df['net'].mean():,.2f}")
print(f"best month            : {best_month} ({monthly.max():,.2f})")
print(f"top category          : {by_cat['revenue'].idxmax()} ({by_cat['share_pct'].max()}% of revenue)")
print(f"IQR outlier orders    : {int(df['out_iqr'].sum())} (kept, flagged)")
print(f"month-1 retention avg : {retention[1].mean():.0f}%")
print("=" * 50)

# 18. Anti-pattern 1: iterrows
# ----------------------------
# - iterrows() builds a whole Series per row: slow, and it can change dtypes
#   (a row mixing int and float becomes all float).
# - FIX: vectorized column math. For conditionals, np.where / np.select.
# - If you truly need a loop, itertuples() is much faster than iterrows().

sample = df[["quantity", "unit_price", "discount_pct"]].head(2000)
slow_total = 0.0
for _, row in sample.iterrows():                       # BAD
    slow_total += row["quantity"] * row["unit_price"] * (1 - row["discount_pct"] / 100)
fast_total = (sample["quantity"] * sample["unit_price"] * (1 - sample["discount_pct"] / 100)).sum()   # GOOD
print("iterrows total:", round(slow_total, 2), "| vectorized total:", round(fast_total, 2), "| same:", bool(np.isclose(slow_total, fast_total)))
print("iterrows row dtype (ints promoted to float):", next(sample.iterrows())[1].dtype)
label = np.select([df["net"] < 50, df["net"] < 200], ["small", "medium"], default="large")
print("np.select replaces an if/elif loop:", pd.Series(label).value_counts().sort_index().to_dict())

# 19. Anti-pattern 2: Chained Assignment
# ----------------------------
# - df[mask]["col"] = value changes a TEMPORARY copy, so the original does not
#   change (and pandas may warn). In pandas 3 / copy-on-write it never works.
# - FIX: one .loc call: df.loc[mask, "col"] = value.
# - When you slice and then edit, take an explicit .copy() so your intent is clear.
# - Here the warning is shown safely by catching it; we do not let it print.

import warnings

demo = pd.DataFrame({"qty": [1, 2, 3, 4], "flag": ["no"] * 4})
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    demo[demo["qty"] > 2]["flag"] = "big"               # BAD: edits a temporary copy
print("after chained assignment:", demo["flag"].tolist(), "(unchanged!)")
print("pandas warned about it:", any("SettingWithCopy" in type(w.message).__name__ for w in caught))
demo.loc[demo["qty"] > 2, "flag"] = "big"               # GOOD
print("after .loc assignment  :", demo["flag"].tolist())
subset = demo[demo["qty"] > 1].copy()                  # explicit copy before editing
subset["flag"] = "edited"
print("explicit copy edits subset only; original flags:", demo["flag"].tolist())

# 20. Anti-pattern 3: concat Inside a Loop
# ----------------------------
# - Each pd.concat copies ALL data so far: the loop is O(n^2).
# - FIX: collect pieces in a plain list, call pd.concat ONCE at the end.
# - Same idea for building a DataFrame row by row: collect dicts/tuples in a
#   list, build the DataFrame once.

import time

pieces = [pd.DataFrame({"i": [k], "sq": [k * k]}) for k in range(300)]
bad = pd.DataFrame({"i": [], "sq": []})
for p in pieces:                                       # BAD: copy on every pass
    bad = pd.concat([bad, p], ignore_index=True)
good = pd.concat(pieces, ignore_index=True)            # GOOD: one concat
print("same values:", bad["sq"].astype(int).tolist() == good["sq"].tolist(), "| rows:", len(good))
rows = [{"i": k, "sq": k * k} for k in range(300)]     # GOOD for row-wise building
print("list of dicts -> one DataFrame:", pd.DataFrame(rows).shape)
print("note: the 'bad' frame's dtype drifted to", bad["sq"].dtype, "while the good one is", good["sq"].dtype)

# 21. Anti-pattern 4: apply for Something Vectorizable
# ----------------------------
# - df.apply(func, axis=1) and Series.apply(lambda) run Python once per row.
# - If a built-in column operation exists (arithmetic, .str, .dt, np.where,
#   map with a dict, merge), it runs in compiled code and is far faster.
# - apply IS right when logic truly cannot be expressed column-wise.
# - Check equality of both approaches before you swap one for the other.

t0 = time.perf_counter()
slow = df.apply(lambda r: r["quantity"] * r["unit_price"], axis=1)       # BAD
t_slow = time.perf_counter() - t0
t0 = time.perf_counter()
fast = df["quantity"] * df["unit_price"]                                # GOOD
t_fast = time.perf_counter() - t0
print("identical results:", bool(np.allclose(slow, fast)))
print("vectorized faster than apply(axis=1):", t_fast < t_slow)   # boolean only, keeps output deterministic
print("Series.apply(lambda) for text -> use .str:",
      df["category"].astype(str).apply(lambda s: s.upper()).equals(df["category"].astype(str).str.upper()))
price_tier = df["unit_price"].map(lambda p: "premium" if p >= 80 else "regular")
price_tier2 = pd.Series(np.where(df["unit_price"] >= 80, "premium", "regular"), index=df.index)
print("lambda vs np.where same:", price_tier.equals(price_tier2), "->", price_tier2.value_counts().sort_index().to_dict())
print("Rule of thumb: reach for apply last, not first.")
