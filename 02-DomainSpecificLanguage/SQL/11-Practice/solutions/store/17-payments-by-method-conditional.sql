-- Title: Payments by method, conditional counts
-- Level: medium
-- Task: Per payment method return method, paid_count (payments with status 'paid'),
--   refunded_count (status 'refunded'), paid_total (sum of amount of the 'paid' payments,
--   ROUND(x, 2)). Sort by method.
-- Hint: SUM(CASE WHEN ... THEN 1 ELSE 0 END): see 02-Querying/02-Aggregation-And-Grouping and
--   04-Patterns/03-Pivot-Unpivot-And-Crosstabs
-- Ordered: yes

SELECT method,
       SUM(status = 'paid') AS paid_count,
       SUM(status = 'refunded') AS refunded_count,
       ROUND(SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END), 2) AS paid_total
FROM payments
GROUP BY method
ORDER BY method;
