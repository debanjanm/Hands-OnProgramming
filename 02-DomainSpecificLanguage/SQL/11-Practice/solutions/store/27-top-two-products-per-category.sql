-- Title: Top 2 products per category, ties kept
-- Level: hard
-- Task: Units sold of a product = SUM(quantity) over its order_items whose order is not cancelled
--   (products with no such sales are ignored). Within each products.category_id rank products by
--   units descending using RANK() and keep rank <= 2, so ties for 2nd place are all kept. Return
--   category_id, product_id, units, rnk. Sort by category_id, rnk, product_id.
-- Hint: see 04-Patterns/01-Top-N-And-Ranking-Patterns (RANK vs ROW_NUMBER vs DENSE_RANK)
-- Ordered: yes

WITH sales AS (
  SELECT p.category_id, p.product_id, SUM(i.quantity) AS units
  FROM order_items i
  JOIN orders o ON o.order_id = i.order_id
  JOIN products p ON p.product_id = i.product_id
  WHERE o.status <> 'cancelled'
  GROUP BY p.category_id, p.product_id
),
ranked AS (
  SELECT *, RANK() OVER (PARTITION BY category_id ORDER BY units DESC) AS rnk FROM sales
)
SELECT category_id, product_id, units, rnk
FROM ranked
WHERE rnk <= 2
ORDER BY category_id, rnk, product_id;
