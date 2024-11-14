-------------------------------
-- Studying index impact, part (a): first version for distinctStatesPerYear.
-------------------------------

-- Function that counts the number of distinct states from wich at least
-- one client from a given country has made an order in the given year.
CREATE OR REPLACE FUNCTION distinctStatesPerYear(IN customer_country VARCHAR(50), order_year INT)
RETURNS BIGINT AS $$
BEGIN
    RETURN (
        SELECT COUNT(DISTINCT(c.state)) :: BIGINT
        FROM customers c
        JOIN orders o ON c.customerid = o.customerid
        WHERE c.country = customer_country AND EXTRACT(YEAR FROM o.orderdate) = order_year
    );
END;
$$ LANGUAGE plpgsql;

SELECT distinctStatesPerYear('Peru', 2017);

-------------------------------
-- Studying index impact, part (b): studying execution plan with EXPLAIN.
-------------------------------

EXPLAIN
SELECT COUNT(DISTINCT(c.state)) :: BIGINT
FROM customers c
JOIN orders o ON c.customerid = o.customerid
WHERE c.country = 'Peru' AND EXTRACT(YEAR FROM o.orderdate) = 2017;

-------------------------------
-- Studying index impact, parts (c), (d), (e) and (f): identifying indexes
-- that potentially improve the query's performance.
-------------------------------

-- Comment/Uncomment SQL lines to create/destroy indexes.

-- Adding an index on customers to accelerate the search for a certain
-- country. Showed little to no improvement.
-- DROP INDEX IF EXISTS idx_customers_country;
-- CREATE INDEX idx_customers_country ON customers (country);

-- Adding an index on customers to accelerate the search for a certain
-- country and state. Shows considerable improvement, ~10ms.
DROP INDEX IF EXISTS idx_customers_country_state;
CREATE INDEX idx_customers_country_state ON customers (country, state);

-- Adding an index on orders to accelerate the search for orders made on
-- a certain year. Shows some improvement, ~5/10ms.
-- DROP INDEX IF EXISTS idx_orders_order_year;
-- CREATE INDEX idx_orders_order_year ON orders (EXTRACT(YEAR FROM orderdate));

-- Adding an index on orders to accelerate the join with the customers
-- table by customerid. Shows some improvement, ~5/10ms.
-- DROP INDEX IF EXISTS idx_orders_customerid;
-- CREATE INDEX idx_orders_customerid ON orders (customerid);