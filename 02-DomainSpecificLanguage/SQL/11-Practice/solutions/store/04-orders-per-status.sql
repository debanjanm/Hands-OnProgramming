-- Title: Orders per status
-- Level: easy
-- Task: Count orders per status. Return status, order_count, sorted by order_count descending,
--   ties by status ascending.
-- Hint: see 02-Querying/02-Aggregation-And-Grouping
-- Ordered: yes

SELECT status, COUNT(*) AS order_count
FROM orders
GROUP BY status
ORDER BY order_count DESC, status;
