-- Title: Duplicate customer accounts
-- Level: hard
-- Task: Two customers are duplicates when their e-mail is equal after TRIM and LOWER. In each
--   duplicate group keep the customer with the lowest customer_id. Return one row for every
--   customer that should be removed: customer_id, kept_customer_id (the lowest id of its group),
--   clean_email (TRIM + LOWER). Sort by customer_id.
-- Hint: see 04-Patterns/07-Data-Cleaning-And-Quality-In-SQL and 03-Window-Functions/01-Window-
--   Functions
-- Ordered: yes

WITH clean AS (
  SELECT customer_id, LOWER(TRIM(email)) AS clean_email,
         MIN(customer_id) OVER (PARTITION BY LOWER(TRIM(email))) AS kept_customer_id
  FROM customers
)
SELECT customer_id, kept_customer_id, clean_email
FROM clean
WHERE customer_id <> kept_customer_id
ORDER BY customer_id;
