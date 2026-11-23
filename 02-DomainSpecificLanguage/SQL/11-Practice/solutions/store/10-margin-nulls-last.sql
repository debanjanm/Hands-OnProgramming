-- Title: Margin percent, unknown cost last
-- Level: easy
-- Task: For all products return product_id, name, margin_pct = ROUND((price - cost) * 100.0 /
--   price, 2). When cost is NULL the margin is NULL. Sort by margin_pct descending with the NULL
--   margins at the end (NULLS LAST), ties by product_id ascending.
-- Hint: SQLite supports NULLS LAST: see 01-Basics/04-Math-And-Numbers and 01-Basics/02-Filtering-
--   And-Operators
-- Ordered: yes

SELECT product_id, name,
       ROUND((price - cost) * 100.0 / price, 2) AS margin_pct
FROM products
ORDER BY margin_pct DESC NULLS LAST, product_id;
