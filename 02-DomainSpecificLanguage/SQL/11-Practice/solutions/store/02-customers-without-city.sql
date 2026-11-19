-- Title: Customers with an unknown city
-- Level: easy
-- Task: Find customers whose city is unknown (NULL). Return customer_id, first_name, last_name,
--   sorted by customer_id.
-- Hint: NULL is never equal to anything, even NULL: see 01-Basics/02-Filtering-And-Operators
-- Ordered: yes

SELECT customer_id, first_name, last_name
FROM customers
WHERE city IS NULL
ORDER BY customer_id;
