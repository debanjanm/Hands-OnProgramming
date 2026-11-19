-- Title: Paid revenue pivot: country by payment method
-- Level: hard
-- Task: Pivot paid payments (status 'paid') into one row per customer country (the country of the
--   customer who placed the order; customers with NULL country are excluded) and one column per
--   method. Return country, card, paypal, upi, bank_transfer where each is SUM(amount) for that
--   method, ROUND(x, 2), and 0 when the country has no such payments. Sort by country.
-- Hint: see 04-Patterns/03-Pivot-Unpivot-And-Crosstabs
-- Ordered: yes

SELECT c.country,
       ROUND(SUM(CASE WHEN p.method = 'card'          THEN p.amount ELSE 0 END), 2) AS card,
       ROUND(SUM(CASE WHEN p.method = 'paypal'        THEN p.amount ELSE 0 END), 2) AS paypal,
       ROUND(SUM(CASE WHEN p.method = 'upi'           THEN p.amount ELSE 0 END), 2) AS upi,
       ROUND(SUM(CASE WHEN p.method = 'bank_transfer' THEN p.amount ELSE 0 END), 2) AS bank_transfer
FROM payments p
JOIN orders o ON o.order_id = p.order_id
JOIN customers c ON c.customer_id = o.customer_id
WHERE p.status = 'paid' AND c.country IS NOT NULL
GROUP BY c.country
ORDER BY c.country;
