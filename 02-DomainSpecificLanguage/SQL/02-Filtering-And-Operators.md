# Filtering & Operators — Notes

## What this covers
The operators you use inside `WHERE`: comparisons, AND/OR/NOT, pattern matching, IN, BETWEEN, NULL checks, and CASE WHEN.

## Key points
- Comparison operators: `=`, `!=`/`<>`, `<`, `>`, `<=`, `>=`. SQLite has no real boolean type — comparisons return 0/1.
- Precedence, highest to lowest: `NOT`, then `AND`, then `OR` — parenthesize when mixing AND/OR.
- `LIKE` is case-insensitive (ASCII), `%` matches any run of chars, `_` matches exactly one.
- `GLOB` is case-sensitive, Unix-style: `*` = any run, `?` = one char, `[abc]` = character class.
- `IN (...)` is shorthand for a chain of OR'd equality checks; also accepts a subquery.
- `BETWEEN x AND y` is inclusive on both ends.
- `IS NULL` / `IS NOT NULL` are the only correct way to test for NULL.
- `CASE WHEN ... THEN ... ELSE ... END` is an expression (evaluates to one value per row), not a control-flow statement — usable in SELECT, WHERE, ORDER BY, etc. First matching branch wins, top to bottom.

## Gotchas (the part worth revising twice)
- `col = NULL` never matches anything, ever — NULL means "unknown," so any comparison with it (`=`, `!=`, `<`...) evaluates to NULL, and the row gets dropped. Always use `IS NULL`.
- Mixing `AND`/`OR` without parentheses is a classic bug: `WHERE dept = 'Engineering' AND salary > 80000 OR dept = 'Sales'` reads as `(dept = 'Engineering' AND salary > 80000) OR dept = 'Sales'` — not "Engineering or Sales, with salary > 80000" like it looks at a glance.
- `LIKE` vs `GLOB` case sensitivity is easy to mix up — `LIKE` ignores case, `GLOB` doesn't.
- `CASE` with no matching branch and no `ELSE` returns `NULL`, not an error.

## When it matters
Any time a query needs to slice rows by more than a simple equality — real WHERE clauses almost always combine a few of these.

## One-line recap example
```sql
SELECT first_name FROM employees
WHERE dept IN ('Sales', 'Marketing')
  AND manager_id IS NOT NULL;
```
