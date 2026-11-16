# Data Modification — Notes

## What this covers
Changing data after it's inserted: UPDATE, DELETE, upsert with INSERT ... ON CONFLICT, and adding/dropping columns with ALTER TABLE.

## Key points
- `UPDATE table SET col = val WHERE ...` — WHERE scopes which rows change; multiple columns can be set in one statement, comma-separated.
- `DELETE FROM table WHERE ...` removes matching rows but keeps the table/schema itself (unlike `DROP TABLE`).
- `INSERT ... ON CONFLICT (col) DO UPDATE SET ...` is an upsert: insert the row, or update the existing one if it conflicts with a UNIQUE/PRIMARY KEY.
- `excluded.column` inside the `DO UPDATE` clause refers to the value that would have been inserted.
- `ALTER TABLE` in SQLite supports only: `RENAME TO`, `RENAME COLUMN`, `ADD COLUMN`, and (since 3.35.0, 2021) `DROP COLUMN`.
- `ADD COLUMN` rules: the new column can't be PRIMARY KEY or UNIQUE, and if NOT NULL it must have a non-NULL DEFAULT so existing rows can be backfilled.

## Gotchas (the part worth revising twice)
- `UPDATE`/`DELETE` with no `WHERE` touches every row — always run the equivalent `SELECT` first to sanity-check which rows will be affected.
- SQLite's `ALTER TABLE` is much more limited than Postgres/MySQL — you can't change a column's type or add/remove a constraint on an existing column directly. The workaround (pre-3.35 for DROP COLUMN, and still the only option for type/constraint changes): create a new table without the offending column/constraint, copy the data across, drop the old table, rename the new one.
- Forgetting `excluded.` in an upsert's `DO UPDATE` clause is an easy mistake — it's the only way to reference the value that was about to be inserted.

## When it matters
Any real application beyond read-only queries — upserts especially, for "insert if new, update if it already exists" without a separate SELECT-then-branch round trip.

## One-line recap example
```sql
INSERT INTO products (sku, name, price) VALUES ('SKU-1', 'Widget', 8.49)
ON CONFLICT (sku) DO UPDATE SET price = excluded.price;
```
