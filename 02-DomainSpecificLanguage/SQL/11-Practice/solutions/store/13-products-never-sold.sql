-- Title: Products never sold
-- Level: medium
-- Task: Find products that appear in no order_items row. Return product_id, name, sorted by
--   product_id.
-- Hint: beware NOT IN with NULLs; NOT EXISTS is safest: see 02-Querying/03-Subqueries-And-CTEs
-- Ordered: yes

SELECT p.product_id, p.name
FROM products p
WHERE NOT EXISTS (SELECT 1 FROM order_items i WHERE i.product_id = p.product_id)
ORDER BY p.product_id;
