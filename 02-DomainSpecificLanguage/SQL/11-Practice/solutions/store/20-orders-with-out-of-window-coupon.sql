-- Title: Coupons used outside their validity window
-- Level: medium
-- Task: Find orders whose coupon was used on an order_date before the coupon's valid_from or
--   after its valid_to (bounds inclusive, ISO text compares correctly). Return order_id, code,
--   order_date, sorted by order_id.
-- Hint: see 02-Querying/01-Joins and 01-Basics/05-Dates-And-Times
-- Ordered: yes

SELECT o.order_id, c.code, o.order_date
FROM orders o
JOIN coupons c ON c.coupon_id = o.coupon_id
WHERE o.order_date < c.valid_from OR o.order_date > c.valid_to
ORDER BY o.order_id;
