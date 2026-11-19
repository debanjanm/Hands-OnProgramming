-- Title: Customer funnel
-- Level: hard
-- Task: Build a funnel over all customers, each stage a subset of the previous one. Stage 1
--   'signed_up': every customer. Stage 2 'ordered': of those, customers with at least one order
--   (any status). Stage 3 'paid': of those, customers with a payment of status 'paid' on one of
--   their orders. Stage 4 'delivered': of those, customers with an order whose status is
--   'delivered'. Stage 5 'reviewed': of those, customers who wrote a review with a non-NULL
--   rating. Return stage_no (1-5), stage (the quoted names), customers (count), pct_of_signups
--   (ROUND(100.0 * customers / stage-1 count, 2)). Sort by stage_no.
-- Hint: per-customer flags in a CTE, then UNION ALL one row per stage: see
--   04-Patterns/05-Cohorts-Retention-And-Funnels
-- Ordered: yes

WITH f AS (
  SELECT c.customer_id,
         EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id) AS ordered,
         EXISTS (SELECT 1 FROM orders o JOIN payments p ON p.order_id = o.order_id
                 WHERE o.customer_id = c.customer_id AND p.status = 'paid') AS paid,
         EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id AND o.status = 'delivered') AS delivered,
         EXISTS (SELECT 1 FROM reviews r WHERE r.customer_id = c.customer_id AND r.rating IS NOT NULL) AS reviewed
  FROM customers c
),
stages AS (
  SELECT 1 AS stage_no, 'signed_up' AS stage, COUNT(*) AS customers FROM f
  UNION ALL SELECT 2, 'ordered',   COUNT(*) FROM f WHERE ordered
  UNION ALL SELECT 3, 'paid',      COUNT(*) FROM f WHERE ordered AND paid
  UNION ALL SELECT 4, 'delivered', COUNT(*) FROM f WHERE ordered AND paid AND delivered
  UNION ALL SELECT 5, 'reviewed',  COUNT(*) FROM f WHERE ordered AND paid AND delivered AND reviewed
)
SELECT stage_no, stage, customers,
       ROUND(100.0 * customers / (SELECT customers FROM stages WHERE stage_no = 1), 2) AS pct_of_signups
FROM stages
ORDER BY stage_no;
