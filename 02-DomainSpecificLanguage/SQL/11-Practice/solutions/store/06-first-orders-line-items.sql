-- Title: Line items of the first ten orders
-- Level: easy
-- Task: For order_items belonging to orders 1 to 10, return order_id, product_name
--   (products.name), quantity, line_total (ROUND(quantity * unit_price, 2)). Sort by item_id
--   ascending.
-- Hint: see 02-Querying/01-Joins (INNER JOIN)
-- Ordered: yes

SELECT i.order_id, p.name AS product_name, i.quantity,
       ROUND(i.quantity * i.unit_price, 2) AS line_total
FROM order_items i
JOIN products p ON p.product_id = i.product_id
WHERE i.order_id BETWEEN 1 AND 10
ORDER BY i.item_id;
