-- Title: Signup cohort, next-month retention
-- Level: hard
-- Task: Cohort = calendar month of signup_date ('YYYY-MM', column cohort_month). For each cohort
--   return cohort_month, cohort_size (customers in it), retained (customers of the cohort with at
--   least one non-cancelled order placed in the calendar month right after their signup month),
--   retention_pct = ROUND(100.0 * retained / cohort_size, 2). Include cohorts with zero retained.
--   Sort by cohort_month.
-- Hint: see 04-Patterns/05-Cohorts-Retention-And-Funnels
-- Ordered: yes

WITH c AS (
  SELECT customer_id, strftime('%Y-%m', signup_date) AS cohort_month,
         strftime('%Y-%m', signup_date, 'start of month', '+1 month') AS next_month
  FROM customers
)
SELECT c.cohort_month,
       COUNT(*) AS cohort_size,
       SUM(EXISTS (SELECT 1 FROM orders o
                   WHERE o.customer_id = c.customer_id AND o.status <> 'cancelled'
                     AND strftime('%Y-%m', o.order_date) = c.next_month)) AS retained,
       ROUND(100.0 * SUM(EXISTS (SELECT 1 FROM orders o
                   WHERE o.customer_id = c.customer_id AND o.status <> 'cancelled'
                     AND strftime('%Y-%m', o.order_date) = c.next_month)) / COUNT(*), 2) AS retention_pct
FROM c
GROUP BY c.cohort_month
ORDER BY c.cohort_month;
