-- Title: Return rate by category
-- Level: medium
-- Task: Per product category (products.category_id, show categories.name as category) return
--   category, items_sold (number of order_items rows), items_returned (number of those rows that
--   have a returns row), return_rate_pct = ROUND(100.0 * items_returned / items_sold, 2). Keep
--   only categories with at least one returned item. Sort by the rounded return_rate_pct descending, ties by
--   category ascending.
-- Hint: see 02-Querying/01-Joins (LEFT JOIN) and 02-Querying/02-Aggregation-And-Grouping
-- Ordered: yes

SELECT c.name AS category,
       COUNT(*) AS items_sold,
       COUNT(r.return_id) AS items_returned,
       ROUND(100.0 * COUNT(r.return_id) / COUNT(*), 2) AS return_rate_pct
FROM order_items i
JOIN products p ON p.product_id = i.product_id
JOIN categories c ON c.category_id = p.category_id
LEFT JOIN returns r ON r.item_id = i.item_id
GROUP BY c.category_id, c.name
HAVING COUNT(r.return_id) >= 1
ORDER BY return_rate_pct DESC, category;
