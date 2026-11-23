-- Dataset: store  (an online shop, ~18 months: 2023-01 .. 2024-06)
-- Pure SQL, deterministic: no random(), everything derives from row numbers and small lookup lists.
-- Dirty on purpose: duplicate e-mails differing by case, NULL city/cost/rating, cancelled and
-- pending orders, orders without items, products never sold, customers who never ordered,
-- coupons used outside their validity window, padded / mixed-case text.

PRAGMA foreign_keys = ON;

CREATE TABLE categories (
  category_id INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  parent_id   INTEGER REFERENCES categories(category_id)   -- NULL = top level
);
INSERT INTO categories VALUES
 (1,'Electronics',NULL),(2,'Home',NULL),(3,'Books',NULL),(4,'Clothing',NULL),(15,'Toys',NULL),
 (5,'Phones',1),(6,'Laptops',1),(7,'Audio',1),(8,'Kitchen',2),(9,'Furniture',2),
 (10,'Fiction',3),(11,'Non-fiction',3),(12,'Phone Accessories',5),(13,'Mens',4),(14,'Womens',4);

CREATE TABLE coupons (
  coupon_id    INTEGER PRIMARY KEY,
  code         TEXT NOT NULL UNIQUE,
  discount_pct INTEGER NOT NULL,
  valid_from   TEXT NOT NULL,
  valid_to     TEXT NOT NULL
);
INSERT INTO coupons VALUES
 (1,'WELCOME10',10,'2023-01-01','2023-12-31'),
 (2,'SUMMER15',15,'2023-06-01','2023-08-31'),
 (3,'LOYAL20',20,'2023-01-01','2024-12-31'),
 (4,'EXPIRED5',5,'2022-01-01','2022-12-31'),
 (5,'BLACKFRI25',25,'2023-11-24','2023-11-27'),
 (6,'UNUSED30',30,'2024-01-01','2024-12-31');

CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  first_name  TEXT NOT NULL,
  last_name   TEXT NOT NULL,
  email       TEXT NOT NULL,
  city        TEXT,                                     -- NULL for some
  country     TEXT,
  signup_date TEXT NOT NULL,
  referred_by INTEGER REFERENCES customers(customer_id) -- NULL = organic signup
);
WITH RECURSIVE n(i) AS (SELECT 0 UNION ALL SELECT i+1 FROM n WHERE i < 39),
fn(k,v) AS (VALUES (0,'Anna'),(1,'Ben'),(2,'Carla'),(3,'David'),(4,'Elena'),(5,'Farid'),(6,'Grace'),(7,'Hiro'),(8,'Isla'),(9,'Jonas')),
ln(k,v) AS (VALUES (0,'Meyer'),(1,'Rossi'),(2,'Dubois'),(3,'Smith'),(4,'Garcia'),(5,'Nowak'),(6,'Khan'),(7,'Silva')),
ct(k,city,country) AS (VALUES (0,'Berlin','Germany'),(1,'Munich','Germany'),(2,'Paris','France'),(3,'Lyon','France'),
                              (4,'London','UK'),(5,'Madrid','Spain'),(6,'Rome','Italy'),(7,'Vienna','Austria')),
dm(k,v) AS (VALUES (0,'mail.example'),(1,'post.example'),(2,'web.example'))
INSERT INTO customers
SELECT i+1, fn.v, ln.v,
       lower(fn.v)||'.'||lower(ln.v)||(i+1)||'@'||dm.v,
       CASE WHEN i % 11 = 10 THEN NULL ELSE ct.city END,
       CASE WHEN i % 11 = 10 THEN NULL ELSE ct.country END,
       date('2022-12-01', '+'||((i*37) % 400)||' days'),
       CASE WHEN i % 4 IN (0,1) AND i >= 4 THEN i - 3 END      -- chains: 5<-1, 9<-5 ... and 6<-2 ...
FROM n JOIN fn ON fn.k = i % 10
       JOIN ln ON ln.k = (i/10 + i*3) % 8
       JOIN ct ON ct.k = (i*3) % 8
       JOIN dm ON dm.k = i % 3;
-- duplicate sign-ups: same e-mail as customers 3, 9, 15, 21 but different case / padding
UPDATE customers SET email = upper((SELECT c.email FROM customers c WHERE c.customer_id = customers.customer_id - 34))
 WHERE customer_id IN (35,36,37);
UPDATE customers SET email = ' ' || (SELECT c.email FROM customers c WHERE c.customer_id = customers.customer_id - 34) || ' '
 WHERE customer_id = 38;
-- text oddities
UPDATE customers SET last_name = last_name || ' ' WHERE customer_id IN (6, 14);
UPDATE customers SET city = lower(city)           WHERE customer_id IN (7, 19);
UPDATE customers SET city = upper(city)           WHERE customer_id = 8;

CREATE TABLE products (
  product_id   INTEGER PRIMARY KEY,
  name         TEXT NOT NULL,
  category_id  INTEGER NOT NULL REFERENCES categories(category_id),
  price        REAL NOT NULL,
  cost         REAL,                                   -- NULL for some
  active       INTEGER NOT NULL DEFAULT 1,
  created_date TEXT NOT NULL
);
WITH RECURSIVE n(i) AS (SELECT 0 UNION ALL SELECT i+1 FROM n WHERE i < 59),
adj(k,v) AS (VALUES (0,'Basic'),(1,'Pro'),(2,'Mini'),(3,'Eco'),(4,'Deluxe'),(5,'Classic')),
leaf(k,cat,noun) AS (VALUES (0,5,'Phone'),(1,6,'Laptop'),(2,7,'Headphones'),(3,8,'Blender'),(4,9,'Desk'),
                            (5,10,'Novel'),(6,11,'Biography'),(7,12,'Phone Case'),(8,13,'T-Shirt'),(9,14,'Dress'))
INSERT INTO products
SELECT i+1,
       adj.v||' '||CASE WHEN i % 15 = 0 THEN 'Lamp' ELSE leaf.noun END,
       CASE WHEN i % 15 = 0 THEN 2 ELSE leaf.cat END,
       round(9.99 + 10*((i*7) % 13) + CASE WHEN i % 10 IN (0,1) THEN 200 ELSE 0 END, 2),
       CASE WHEN i % 17 = 16 THEN NULL
            ELSE round((9.99 + 10*((i*7) % 13) + CASE WHEN i % 10 IN (0,1) THEN 200 ELSE 0 END) * (0.5 + (i % 4)*0.1), 2) END,
       CASE WHEN i % 13 = 12 THEN 0 ELSE 1 END,
       date('2022-06-01', '+'||((i*11) % 200)||' days')
FROM n JOIN adj ON adj.k = i/10 JOIN leaf ON leaf.k = i % 10;

CREATE TABLE orders (
  order_id    INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
  order_date  TEXT NOT NULL,
  status      TEXT NOT NULL CHECK (status IN ('pending','shipped','delivered','cancelled')),
  coupon_id   INTEGER REFERENCES coupons(coupon_id)
);
WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i+1 FROM n WHERE i < 200)
INSERT INTO orders
SELECT i,
       (i*7 + (i*i)/11) % 37 + 1,
       date('2023-01-01', '+'||((i*53) % 545)||' days'),
       CASE i % 10 WHEN 0 THEN 'cancelled' WHEN 1 THEN 'pending' WHEN 2 THEN 'shipped' WHEN 3 THEN 'shipped' ELSE 'delivered' END,
       CASE WHEN i % 6 = 0 THEN 1 + (i/6) % 5 END
FROM n;
-- nobody orders before signing up
UPDATE orders SET order_date = date((SELECT signup_date FROM customers c WHERE c.customer_id = orders.customer_id), '+'||(order_id % 20)||' days')
 WHERE order_date < (SELECT signup_date FROM customers c WHERE c.customer_id = orders.customer_id);

CREATE TABLE order_items (
  item_id    INTEGER PRIMARY KEY,
  order_id   INTEGER NOT NULL REFERENCES orders(order_id),
  product_id INTEGER NOT NULL REFERENCES products(product_id),
  quantity   INTEGER NOT NULL CHECK (quantity > 0),
  unit_price REAL NOT NULL                              -- price actually charged (may differ from products.price)
);
WITH RECURSIVE j(j) AS (SELECT 1 UNION ALL SELECT j+1 FROM j WHERE j < 4)
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT o.order_id,
       1 + (o.order_id*5 + j.j*17 + o.order_id/3) % 54,
       1 + (o.order_id + j.j) % 3,
       0
FROM orders o JOIN j ON j.j <= 1 + (o.order_id % 7) % 4
WHERE o.order_id % 25 <> 0                              -- every 25th order has no items
ORDER BY o.order_id, j.j;
UPDATE order_items SET unit_price = round((SELECT price FROM products p WHERE p.product_id = order_items.product_id)
                                          * CASE WHEN item_id % 9 = 0 THEN 0.9 ELSE 1 END, 2);

CREATE TABLE payments (
  payment_id INTEGER PRIMARY KEY,
  order_id   INTEGER NOT NULL REFERENCES orders(order_id),
  method     TEXT NOT NULL,
  amount     REAL NOT NULL,                              -- items total minus coupon discount
  paid_date  TEXT NOT NULL,
  status     TEXT NOT NULL CHECK (status IN ('paid','refunded'))
);
INSERT INTO payments (order_id, method, amount, paid_date, status)
SELECT o.order_id,
       CASE o.order_id % 4 WHEN 0 THEN 'card' WHEN 1 THEN 'paypal' WHEN 2 THEN 'upi' ELSE 'bank_transfer' END,
       round(t.gross * (1 - COALESCE(cp.discount_pct, 0)/100.0), 2),
       date(o.order_date, '+'||(o.order_id % 3)||' days'),
       CASE WHEN o.status = 'cancelled' THEN 'refunded' ELSE 'paid' END
FROM orders o
JOIN (SELECT order_id, SUM(quantity*unit_price) AS gross FROM order_items GROUP BY order_id) t ON t.order_id = o.order_id
LEFT JOIN coupons cp ON cp.coupon_id = o.coupon_id
WHERE o.status IN ('shipped','delivered') OR (o.status = 'cancelled' AND o.order_id % 20 = 0)
ORDER BY o.order_id;

CREATE TABLE reviews (
  review_id   INTEGER PRIMARY KEY,
  product_id  INTEGER NOT NULL REFERENCES products(product_id),
  customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
  rating      INTEGER CHECK (rating BETWEEN 1 AND 5),    -- NULL = left a comment only
  review_date TEXT NOT NULL,
  title       TEXT
);
WITH RECURSIVE n(k) AS (SELECT 1 UNION ALL SELECT k+1 FROM n WHERE k < 120),
tt(k,v) AS (VALUES (0,'Great value'),(1,'works fine'),(2,'  Not as described'),(3,'LOVE IT'),(4,'Broke after a week'),(5,NULL))
INSERT INTO reviews
SELECT n.k, 1 + (n.k*7) % 50, 1 + (n.k*11) % 34,
       CASE WHEN n.k % 9 = 0 THEN NULL ELSE 1 + (n.k*n.k + n.k/3) % 5 END,
       date('2023-02-01', '+'||((n.k*17) % 500)||' days'),
       tt.v
FROM n JOIN tt ON tt.k = n.k % 6;

CREATE TABLE returns (
  return_id   INTEGER PRIMARY KEY,
  item_id     INTEGER NOT NULL REFERENCES order_items(item_id),
  return_date TEXT NOT NULL,
  reason      TEXT NOT NULL
);
WITH rs(k,v) AS (VALUES (0,'defective'),(1,'wrong size'),(2,'changed mind'),(3,'arrived late'))
INSERT INTO returns (item_id, return_date, reason)
SELECT i.item_id, date(o.order_date, '+'||(5 + i.item_id % 10)||' days'), rs.v
FROM order_items i JOIN orders o ON o.order_id = i.order_id JOIN rs ON rs.k = i.item_id % 4
WHERE o.status = 'delivered' AND i.item_id % 19 = 0
ORDER BY i.item_id;
