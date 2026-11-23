-- Title: Running paid revenue and share of total
-- Level: hard
-- Task: Group payments with status 'paid' by the month of paid_date ('YYYY-MM', column month).
--   Return month, revenue (sum of amount, ROUND(x, 2)), running_revenue (cumulative sum over
--   months in order, ROUND(x, 2)), pct_of_total (the month's revenue as a percentage of all paid
--   revenue, ROUND(x, 2)). Compute the running and percent values from unrounded sums. Sort by
--   month.
-- Hint: see 03-Window-Functions/01-Window-Functions (frames) and 04-Patterns/04-Time-Series-
--   Patterns
-- Ordered: yes

WITH monthly AS (
  SELECT strftime('%Y-%m', paid_date) AS month, SUM(amount) AS revenue
  FROM payments
  WHERE status = 'paid'
  GROUP BY month
)
SELECT month,
       ROUND(revenue, 2) AS revenue,
       ROUND(SUM(revenue) OVER (ORDER BY month), 2) AS running_revenue,
       ROUND(100.0 * revenue / SUM(revenue) OVER (), 2) AS pct_of_total
FROM monthly
ORDER BY month;
