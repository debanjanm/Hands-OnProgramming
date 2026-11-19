-- Title: Categories with at least 5 products
-- Level: medium
-- Task: Using products.category_id directly (no category tree), find categories that have at
--   least 5 products. Return category_id, product_count, avg_price (ROUND(AVG(price), 2)), sorted
--   by category_id.
-- Hint: HAVING filters groups, WHERE filters rows: see 02-Querying/02-Aggregation-And-Grouping
-- Ordered: yes

SELECT category_id, COUNT(*) AS product_count, ROUND(AVG(price), 2) AS avg_price
FROM products
GROUP BY category_id
HAVING COUNT(*) >= 5
ORDER BY category_id;
