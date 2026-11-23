-- Title: Lapsed customers
-- Level: medium
-- Task: A customer is lapsed if their most recent non-cancelled order is before 2024-01-01
--   (customers with no non-cancelled orders are not included). Return customer_id,
--   last_order_date, days_inactive (whole days from last_order_date to '2024-06-30'). Sort by
--   last_order_date ascending, ties by customer_id.
-- Hint: see 02-Querying/02-Aggregation-And-Grouping and 01-Basics/05-Dates-And-Times
-- Ordered: yes

SELECT customer_id,
       MAX(order_date) AS last_order_date,
       CAST(julianday('2024-06-30') - julianday(MAX(order_date)) AS INTEGER) AS days_inactive
FROM orders
WHERE status <> 'cancelled'
GROUP BY customer_id
HAVING MAX(order_date) < '2024-01-01'
ORDER BY last_order_date, customer_id;
