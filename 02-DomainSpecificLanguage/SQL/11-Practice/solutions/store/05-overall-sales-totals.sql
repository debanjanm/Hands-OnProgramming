-- Title: Overall sales totals
-- Level: easy
-- Task: Using order_items only (all orders, whatever their status), return a single row with:
--   line_items (number of order_items rows), units (sum of quantity), gross_revenue (sum of
--   quantity * unit_price, ROUND(x, 2)).
-- Hint: see 02-Querying/02-Aggregation-And-Grouping
-- Ordered: no

SELECT COUNT(*) AS line_items,
       SUM(quantity) AS units,
       ROUND(SUM(quantity * unit_price), 2) AS gross_revenue
FROM order_items;
