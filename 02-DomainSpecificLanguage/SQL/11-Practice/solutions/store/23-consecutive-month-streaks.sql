-- Title: Consecutive-month buying streaks
-- Level: hard
-- Task: A buying month is a calendar month in which a customer placed at least one non-cancelled
--   order. Find every streak of 2 or more consecutive buying months per customer (a streak must
--   be as long as possible, not extendable on either side). Return customer_id, start_month,
--   end_month (both 'YYYY-MM'), months (streak length). Sort by customer_id, then start_month.
-- Hint: classic islands trick, month number minus ROW_NUMBER: see 04-Patterns/02-Gaps-Islands-
--   And-Sessions
-- Ordered: yes

WITH m AS (
  SELECT DISTINCT customer_id,
         CAST(strftime('%Y', order_date) AS INTEGER) * 12 + CAST(strftime('%m', order_date) AS INTEGER) AS mno
  FROM orders
  WHERE status <> 'cancelled'
),
grp AS (
  SELECT customer_id, mno,
         mno - ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY mno) AS g
  FROM m
)
SELECT customer_id,
       printf('%04d-%02d', (MIN(mno) - 1) / 12, (MIN(mno) - 1) % 12 + 1) AS start_month,
       printf('%04d-%02d', (MAX(mno) - 1) / 12, (MAX(mno) - 1) % 12 + 1) AS end_month,
       COUNT(*) AS months
FROM grp
GROUP BY customer_id, g
HAVING COUNT(*) >= 2
ORDER BY customer_id, start_month;
