-- Title: Customers who never ordered
-- Level: medium
-- Task: Find customers with no row in orders at all (any status). Return customer_id, email,
--   sorted by customer_id.
-- Hint: anti-join with NOT EXISTS or LEFT JOIN ... IS NULL: see 02-Querying/01-Joins and
--   02-Querying/03-Subqueries-And-CTEs
-- Ordered: yes

SELECT c.customer_id, c.email
FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)
ORDER BY c.customer_id;
