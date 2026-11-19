-- Title: Customer spend ranking
-- Level: medium
-- Task: Total spend of a customer = sum of payments.amount with status 'paid' on their orders.
--   For customers with at least one paid payment, return customer_id, total_spent (ROUND(x, 2)),
--   spend_rank = RANK() over total_spent descending (compare the rounded values so equal rounded
--   spends tie). Sort by spend_rank, then customer_id.
-- Hint: see 03-Window-Functions/01-Window-Functions (RANK vs ROW_NUMBER)
-- Ordered: yes

WITH spend AS (
  SELECT o.customer_id, ROUND(SUM(p.amount), 2) AS total_spent
  FROM payments p
  JOIN orders o ON o.order_id = p.order_id
  WHERE p.status = 'paid'
  GROUP BY o.customer_id
)
SELECT customer_id, total_spent,
       RANK() OVER (ORDER BY total_spent DESC) AS spend_rank
FROM spend
ORDER BY spend_rank, customer_id;
