# Window Functions — Notes

## What this covers
Functions that compute a value across a "window" of related rows without collapsing them into one row like GROUP BY does: OVER(), ROW_NUMBER, RANK/DENSE_RANK, LAG/LEAD, running totals, and PARTITION BY.

## Key points
- Any function followed by `OVER (...)` is a window function — it keeps every row, but computes its result using a related set of rows (unlike GROUP BY, which collapses rows).
- `ROW_NUMBER() OVER (ORDER BY col)` gives a strictly increasing, unique number per row within the window; ties get arbitrarily distinct numbers.
- `RANK()`: ties share a rank, and the next rank skips ahead by the number of tied rows (1, 2, 2, 4...).
- `DENSE_RANK()`: ties share a rank, but the next rank is always +1, no gaps (1, 2, 2, 3...).
- `LAG(col, n)` / `LEAD(col, n)` pull a value from n rows before/after the current row (default n=1); return NULL at the start/end of the window — avoids a self-join for period-over-period comparisons.
- `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` is the frame clause for a running total ("every row so far").
- `PARTITION BY col` divides rows into independent groups before applying the window function — each partition computed separately, like GROUP BY that doesn't collapse rows.

## Gotchas (the part worth revising twice)
- Window functions don't reduce row count the way GROUP BY does — that's the whole point, but it's easy to expect fewer rows back and be surprised.
- RANK vs DENSE_RANK is a common mix-up: RANK leaves gaps after ties, DENSE_RANK doesn't.
- Forgetting `PARTITION BY` means the window spans the *entire* result set, not per-group — `LAG`/`LEAD`/running totals without partitioning will bleed across groups (e.g. salesperson) that should stay separate.
- `ORDER BY` inside `OVER (...)` controls window row order, and is independent of any outer-query `ORDER BY`.

## When it matters
Rankings, running totals, period-over-period comparisons (this order vs the last one) — anywhere you need a per-row calculation that depends on neighboring rows without losing the row-level detail.

## One-line recap example
```sql
SELECT salesperson, amount,
       RANK() OVER (PARTITION BY region ORDER BY amount DESC) AS rank_in_region
FROM orders;
```
