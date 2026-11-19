-- Title: Price tiers with CASE
-- Level: easy
-- Task: Label every product with a tier: 'budget' if price < 30, 'standard' if price is at least
--   30 and below 100, otherwise 'premium'. Return product_id, name, price, tier, sorted by
--   product_id.
-- Hint: see 01-Basics/02-Filtering-And-Operators (CASE)
-- Ordered: yes

SELECT product_id, name, price,
       CASE WHEN price < 30  THEN 'budget'
            WHEN price < 100 THEN 'standard'
            ELSE 'premium' END AS tier
FROM products
ORDER BY product_id;
