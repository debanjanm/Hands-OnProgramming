# 11-Practice: SQL problems with auto-checking

Hands-on exercises for the SQL track. Each problem is a `.sql` file with a task in its header; you write the
query, `pytest` runs it against a deterministic dataset and compares your rows with the reference answer.
Datasets so far: **store** (30 problems). More datasets (hr, streaming, bank) come later.

## How to use

Run everything from the `SQL` folder:

```bash
pytest 11-Practice                    # check YOUR answers in problems/   (unsolved ones fail with the task + hint)
pytest 11-Practice -k "store and 07"  # one problem
pytest 11-Practice -k store           # one dataset
pytest 11-Practice --solutions        # check the reference answers in solutions/ (should all pass)
```

1. Open `problems/store/NN-slug.sql`, read the `-- Task:` header.
2. Write your query below the header (a single `SELECT`, `WITH ... SELECT` is fine; the last statement that returns rows is checked).
3. Run `pytest 11-Practice -k "store and NN"`. Stuck? Read the Hint, then peek at `solutions/store/NN-slug.sql`.

What is compared: the **rows** of your result against the solution's. The column count must match; column names are
**not** compared (but follow the aliases in the task anyway); floats are rounded to 6 places. If `Ordered: yes` the row
order must match too, otherwise any order is fine. Every problem has two tests: your answer, and an integrity check of
the problem itself (solution returns rows, is deterministic, starter header matches).

## File layout

```
datasets/<name>.sql              pure SQL: CREATE TABLE + deterministic seed data (rebuilt in a fresh in-memory SQLite per query)
solutions/<name>/NN-slug.sql     header + reference query (the header here is the source of truth)
problems/<name>/NN-slug.sql      same header, empty query area: your answer goes here
conftest.py, test_practice.py, pytest.ini   the harness
```

### Problem file format

Leading comment lines `-- Key: value` (continuation lines start with `--` and spaces), then the query:

```sql
-- Title: Active products, priciest first
-- Level: easy                      (easy | medium | hard)
-- Task: What to return, which columns in which order, aliases, sort order, ties, rounding.
--   continuation line
-- Hint: see 01-Basics/02-Filtering-And-Operators
-- Ordered: yes                     (yes = the task states an ORDER BY and row order is checked)

SELECT ...;
```

## Explore the dataset

```bash
sqlite3 :memory: < datasets/store.sql          # loads, then exits: use the next form to stay inside
sqlite3 :memory: ".read datasets/store.sql" -header -column    # then type queries, e.g. SELECT * FROM orders LIMIT 5;
```

(or `sqlite3 /tmp/store.db < datasets/store.sql`, then `sqlite3 -header -column /tmp/store.db`.)

## The `store` dataset

An online shop, orders from 2023-02 to 2024-06 (dates are ISO text `YYYY-MM-DD`): 40 customers, 60 products, 200 orders,
441 order items, 164 payments, 120 reviews, 15 returns, 15 categories, 6 coupons. Generated with recursive CTEs and
lookup lists, no randomness: loading it twice gives identical data.

Intentional traps: customers 35-38 duplicate the e-mails of customers 1-4 (different case / padded spaces); NULL city,
product cost and review rating; padded/mixed-case text (`'Meyer '`, `'paris'`, `'MADRID'`, `'  Not as described'`);
cancelled and pending orders; 8 orders without items; 6 products never sold; 4 customers who never ordered; a coupon
used outside its validity window; unit_price sometimes differs from products.price; a category with no products;
a 3-level category tree and referral chains for recursive queries.

| Table | Columns |
|---|---|
| customers | customer_id PK, first_name, last_name, email, city (NULL), country (NULL), signup_date, referred_by -> customers |
| categories | category_id PK, name, parent_id -> categories (NULL = top level) |
| products | product_id PK, name, category_id -> categories, price, cost (NULL), active (0/1), created_date |
| orders | order_id PK, customer_id -> customers, order_date, status (pending/shipped/delivered/cancelled), coupon_id -> coupons (NULL) |
| order_items | item_id PK, order_id -> orders, product_id -> products, quantity, unit_price (price charged) |
| payments | payment_id PK, order_id -> orders, method (card/paypal/upi/bank_transfer), amount (after coupon), paid_date, status (paid/refunded) |
| reviews | review_id PK, product_id -> products, customer_id -> customers, rating 1-5 (NULL), review_date, title (NULL) |
| returns | return_id PK, item_id -> order_items, return_date, reason |
| coupons | coupon_id PK, code UNIQUE, discount_pct, valid_from, valid_to |

```
categories --< categories (parent_id)           customers --< customers (referred_by)
categories --< products --< order_items >-- orders >-- customers
                  |              |            |  \
                  |              |            |   >-- coupons (optional)
                  |              |            \--< payments
                  |              \--< returns
                  \--< reviews >-- customers
```
(`A --< B` = one A has many B.)

## Problems

| # | Title | Level | Skill |
|---|---|---|---|
| 01 | Active products, priciest first | easy | SELECT, WHERE, ORDER BY |
| 02 | Customers with an unknown city | easy | NULL handling |
| 03 | Phone-like products in a price range | easy | LIKE, BETWEEN |
| 04 | Orders per status | easy | GROUP BY, COUNT |
| 05 | Overall sales totals | easy | Aggregate functions |
| 06 | Line items of the first ten orders | easy | INNER JOIN |
| 07 | Pending orders with customer names | easy | JOIN, string concatenation |
| 08 | Average rating and the NULL trap | easy | NULL in aggregates |
| 09 | Price tiers with CASE | easy | CASE |
| 10 | Margin percent, unknown cost last | easy | NULL ordering, arithmetic |
| 11 | Categories with at least 5 products | medium | GROUP BY + HAVING |
| 12 | Customers who never ordered | medium | Anti-join |
| 13 | Products never sold | medium | Anti-join |
| 14 | Orders above the average order total | medium | CTE + scalar subquery |
| 15 | Monthly revenue of live orders | medium | Dates, GROUP BY |
| 16 | Customer spend ranking | medium | RANK window function |
| 17 | Payments by method, conditional counts | medium | Conditional aggregation |
| 18 | Best rated products | medium | JOIN + GROUP BY + HAVING + NULLs |
| 19 | Days between first and second order | medium | ROW_NUMBER / LAG, dates |
| 20 | Coupons used outside their validity window | medium | Join on a range, dates as text |
| 21 | Return rate by category | medium | LEFT JOIN, multi-table join |
| 22 | Lapsed customers | medium | HAVING with MAX, date arithmetic |
| 23 | Consecutive-month buying streaks | hard | Gaps and islands |
| 24 | Signup cohort, next-month retention | hard | Cohorts and retention |
| 25 | Referral chain from customer 1 | hard | Recursive CTE |
| 26 | Running paid revenue and share of total | hard | Running total, percent of total |
| 27 | Top 2 products per category, ties kept | hard | Top-N per group with ties |
| 28 | Paid revenue pivot: country by payment method | hard | Pivot with conditional aggregation |
| 29 | Duplicate customer accounts | hard | Deduplication |
| 30 | Customer funnel | hard | Funnel analysis |

The table is generated from the problem headers; the Hint of each problem points to the notebook that teaches the skill.
