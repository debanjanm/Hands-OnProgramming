-- Title: Days between first and second order
-- Level: medium
-- Task: For customers with at least two orders (any status), return customer_id,
--   first_order_date, second_order_date, days_between (whole days between the two, second minus
--   first). Order the orders of a customer by order_date, then order_id, to decide which is first
--   and second. Sort by customer_id.
-- Hint: see 03-Window-Functions/01-Window-Functions and 01-Basics/05-Dates-And-Times (julianday)
-- Ordered: yes

WITH numbered AS (
  SELECT customer_id, order_date,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS rn
  FROM orders
)
SELECT a.customer_id, a.order_date AS first_order_date, b.order_date AS second_order_date,
       CAST(julianday(b.order_date) - julianday(a.order_date) AS INTEGER) AS days_between
FROM numbered a
JOIN numbered b ON b.customer_id = a.customer_id AND b.rn = 2
WHERE a.rn = 1
ORDER BY a.customer_id;
