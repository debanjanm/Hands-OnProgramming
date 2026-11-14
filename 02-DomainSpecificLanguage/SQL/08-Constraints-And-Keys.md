# Constraints & Keys — Notes

## What this covers
The database-enforced rules on data: primary keys, foreign keys, UNIQUE, CHECK, NOT NULL, and using indexes with EXPLAIN QUERY PLAN.

## Key points
- Every SQLite table (unless `WITHOUT ROWID`) has a hidden 64-bit `rowid`.
- A column declared exactly `INTEGER PRIMARY KEY` becomes an alias for that rowid — auto-increments on its own, and lookups by it are the fastest possible.
- Foreign keys are declared with `REFERENCES other_table(col)`.
- `UNIQUE` blocks duplicate non-NULL values in a column; the column can still hold NULL.
- `CHECK (expr)` is a row-level rule that must be true (or NULL) for every row — lets the database enforce domain rules directly.
- `NOT NULL` rejects any write that would leave the column NULL; combine with `DEFAULT` for an automatic fallback.
- `CREATE INDEX ON table(col)` builds a lookup structure so SQLite can find rows without scanning the whole table.
- `EXPLAIN QUERY PLAN` shows how SQLite intends to run a query without running it — "SCAN" means full row-by-row scan, "SEARCH ... USING INDEX" means it used an index.

## Gotchas (the part worth revising twice)
- SQLite parses `FOREIGN KEY` constraints but does **not enforce them by default** — you must run `PRAGMA foreign_keys = ON;` per connection, every time, or bogus references insert silently.
- `INTEGER PRIMARY KEY` (exact wording) is the special rowid-alias case; `BIGINT PRIMARY KEY` or a composite `PRIMARY KEY` does NOT get this behavior — it becomes a normal indexed column instead.
- `UNIQUE` treats multiple NULLs as all distinct from each other — inserting NULL twice into a UNIQUE column is allowed, since NULL is never "equal" to anything, not even another NULL.
- Because SQLite's dynamic typing lets wrong-type data slip into a column silently (see file 01), `CHECK` is your real defense against that class of bug — it's not just for numeric ranges.

## When it matters
Any schema meant to survive real use — constraints are what stop bad data from ever landing, instead of relying on application code to catch it every time.

## One-line recap example
```sql
PRAGMA foreign_keys = ON;   -- must be set every connection, SQLite ignores FKs otherwise

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    price      REAL NOT NULL CHECK (price >= 0)
);
```
