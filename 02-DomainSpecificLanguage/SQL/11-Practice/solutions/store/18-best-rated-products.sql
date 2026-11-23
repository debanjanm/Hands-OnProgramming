-- Title: Best rated products
-- Level: medium
-- Task: For each product with at least 3 reviews that carry a rating, return product_id, name,
--   rated_reviews (number of reviews with a non-NULL rating), avg_rating (ROUND(AVG(rating), 2)).
--   Sort by the rounded avg_rating descending, ties by product_id ascending.
-- Hint: see 02-Querying/02-Aggregation-And-Grouping
-- Ordered: yes

SELECT p.product_id, p.name, COUNT(r.rating) AS rated_reviews, ROUND(AVG(r.rating), 2) AS avg_rating
FROM products p
JOIN reviews r ON r.product_id = p.product_id
GROUP BY p.product_id, p.name
HAVING COUNT(r.rating) >= 3
ORDER BY avg_rating DESC, p.product_id;
