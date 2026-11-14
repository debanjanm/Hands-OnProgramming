# Joins — Notes

## What this covers
How to combine rows from multiple tables: INNER, LEFT, RIGHT/FULL OUTER, CROSS joins, self-joins, and chaining several joins together.

## Key points
- `INNER JOIN` keeps only rows that match on both sides.
- `LEFT JOIN` keeps every row from the left table; unmatched right-side columns come back NULL.
- `RIGHT JOIN` and `FULL OUTER JOIN` keep unmatched rows from the right side (or both sides).
- `CROSS JOIN` is a cartesian product — every left row paired with every right row, no condition, row count = left × right.
- A self-join joins a table to itself using two aliases — classic case: resolving `manager_id` back into the same `employees` table.
- Multiple `JOIN` clauses can be chained to pull in more than two tables; each is evaluated left to right.

## Gotchas (the part worth revising twice)
- SQLite only added native `RIGHT JOIN` and `FULL OUTER JOIN` in version 3.39.0 (2022) — before that, neither existed. The portable workaround: swap the table order and use `LEFT JOIN` instead of `RIGHT JOIN`.
- `INNER JOIN` silently drops rows with no match on either side — a department with zero employees, or an employee with no department, both vanish. Use `LEFT`/`RIGHT`/`FULL` if you need to see them.
- Self-joins need `LEFT JOIN` (not `INNER`) if you still want to see rows with no match (e.g. employees with no manager) — an `INNER` self-join would drop them.
- `CROSS JOIN` on real (non-trivial) tables is rarely intentional — it's an easy way to accidentally explode row counts if a proper join condition is missing.

## When it matters
Anytime data you need lives in more than one table — which is most of the time in a normalized database (see file 12).

## One-line recap example
```sql
SELECT e.first_name, d.dept_name
FROM employees e
LEFT JOIN departments d ON e.dept_id = d.dept_id;
```
