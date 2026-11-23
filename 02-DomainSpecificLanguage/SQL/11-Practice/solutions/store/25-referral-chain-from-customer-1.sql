-- Title: Referral chain from customer 1
-- Level: hard
-- Task: customers.referred_by points to the customer who referred them. Starting from customer 1,
--   find everyone they referred directly (depth 1) or indirectly (depth 2, 3, ...). Do not
--   include customer 1 itself. Return customer_id, depth, path (the ids from customer 1 down to
--   this customer joined by '>', e.g. '1>5'). Sort by depth ascending, ties by customer_id ascending.
-- Hint: see 04-Patterns/06-Hierarchies-And-Graphs and 02-Querying/03-Subqueries-And-CTEs
-- Ordered: yes

WITH RECURSIVE chain(customer_id, depth, path) AS (
  SELECT customer_id, 1, '1>' || customer_id FROM customers WHERE referred_by = 1
  UNION ALL
  SELECT c.customer_id, ch.depth + 1, ch.path || '>' || c.customer_id
  FROM customers c JOIN chain ch ON c.referred_by = ch.customer_id
)
SELECT customer_id, depth, path FROM chain ORDER BY depth, customer_id;
