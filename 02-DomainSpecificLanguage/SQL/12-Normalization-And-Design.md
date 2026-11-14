# Normalization & Design — Notes

## What this covers
Why you split data into multiple related tables instead of one wide table: 1NF/2NF/3NF explained, plus a runnable before/after example.

## Key points
- **1NF**: every column holds a single atomic value (no comma-separated lists, no repeating groups like product_1/product_2), and every row has a primary key.
- **2NF**: must already be 1NF; every non-key column depends on the *whole* primary key, not just part of it — only matters with a composite key.
- **3NF**: must already be 2NF; no transitive dependencies — a non-key column depends on the primary key directly, not on another non-key column (e.g. storing both `dept_id` and `dept_name` on an employee row is a 3NF violation, since `dept_name` depends on `dept_id`).
- A denormalized "wide" table duplicates facts (customer email, product name) across every row that references them — an update anomaly waiting to happen.
- Normalizing splits that into separate tables (customers, products, orders, order_items) linked by foreign keys, so each fact lives in exactly one place.
- The trade-off: normalized data needs joins to reconstruct the "flat" view; denormalized data needs no joins but risks inconsistent duplicate data on updates.

## Gotchas (the part worth revising twice)
- Normalization isn't free — reconstructing a simple report from normalized tables can mean joining 4+ tables, where the denormalized version was one SELECT. That extra JOIN is the real cost, paid at query time in exchange for safety at update time.
- 2NF violations only exist with composite primary keys — if your table has a single-column primary key, 2NF is automatically satisfied and only 3NF is worth checking.
- Heavily-read, rarely-written reporting tables are sometimes *deliberately* denormalized on purpose — normalization is a default, not a law.

## When it matters
Designing any schema that will be updated over time — the more a fact (like a customer's email) is duplicated across rows, the more ways it can go stale or inconsistent.

## One-line recap example
```sql
-- normalized: each fact stored once, joined back together when needed
SELECT c.name, p.name, oi.quantity
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON oi.product_sku = p.sku;
```
