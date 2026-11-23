-- Title: Pending orders with customer names
-- Level: easy
-- Task: List orders whose status is 'pending'. Return order_id, order_date, customer_name
--   (first_name, a single space, then last_name; do not trim), sorted by order_date ascending,
--   ties by order_id ascending.
-- Hint: see 02-Querying/01-Joins and 01-Basics/03-String-And-Text-Functions (the || operator)
-- Ordered: yes

SELECT o.order_id, o.order_date, c.first_name || ' ' || c.last_name AS customer_name
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.status = 'pending'
ORDER BY o.order_date, o.order_id;
