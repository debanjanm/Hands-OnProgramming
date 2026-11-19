-- Title: Orders above the average order total
-- Level: medium
-- Task: The total of an order is SUM(quantity * unit_price) over its items (before any coupon);
--   orders without items have no total and are ignored. Return order_id, total (ROUND(total, 2))
--   for orders whose total is strictly greater than the average total of all orders that have
--   items (compare the unrounded values). Sort by total descending, ties by order_id ascending.
-- Hint: see 02-Querying/03-Subqueries-And-CTEs
-- Ordered: yes

WITH totals AS (
  SELECT order_id, SUM(quantity * unit_price) AS total
  FROM order_items
  GROUP BY order_id
)
SELECT order_id, ROUND(total, 2) AS total
FROM totals
WHERE total > (SELECT AVG(total) FROM totals)
ORDER BY total DESC, order_id;
