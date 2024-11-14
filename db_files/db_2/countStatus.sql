-------------------------------
-- Studying statistics impact, part (b): studying the
-- given queries.
-------------------------------

-- Original queries

SELECT COUNT(*)
FROM orders
WHERE status is null;

SELECT COUNT(*)
FROM orders
WHERE status='Shipped';

-- Planification obtained with EXPLAIN

EXPLAIN
SELECT COUNT(*)
FROM orders
WHERE status is null;

EXPLAIN
SELECT COUNT(*)
FROM orders
WHERE status='Shipped';

-------------------------------
-- Studying statistics impact, part (d): creating index
-- on orders for the status column.
-------------------------------

DROP INDEX IF EXISTS idx_orders_status;
CREATE INDEX idx_orders_status ON orders (status);

-------------------------------
-- Studying statistics impact, part (e): studying the
-- original queries with the new index.
-------------------------------

EXPLAIN
SELECT COUNT(*)
FROM orders
WHERE status is null;

EXPLAIN
SELECT COUNT(*)
FROM orders
WHERE status='Shipped';

-------------------------------
-- Studying statistics impact, part (f): analyzing the
-- orders table to obtain statistics.
-------------------------------

ANALYZE VERBOSE orders;

-------------------------------
-- Studying statistics impact, part (h): analyzing other
-- queries with statistics already created and comparing
-- them to the original ones.
-------------------------------

EXPLAIN
SELECT COUNT(*)
FROM orders
WHERE status='Paid';

EXPLAIN
SELECT COUNT(*)
FROM orders
WHERE status='Processed';