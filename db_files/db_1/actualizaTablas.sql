-- Remove duplicates from orderdetail table


-- Update the quantity of every product in each order
WITH summed_quantities AS (
	SELECT orderid, prod_id, SUM(quantity) AS total_quantity
	FROM orderdetail
	GROUP BY orderid, prod_id
	HAVING COUNT(*) > 1
)
UPDATE orderdetail AS od
SET quantity = sq.total_quantity
FROM summed_quantities AS sq
WHERE od.orderid = sq.orderid
  AND od.prod_id = sq.prod_id;

-- Delete the duplicate rows, keeping only the row with the minimum ctid
-- and the one reflecting the actual quantity for each product and order
WITH CTE AS (
	SELECT ctid, 
		   ROW_NUMBER() OVER (PARTITION BY orderid, prod_id ORDER BY ctid) AS rn
	FROM orderdetail
)
DELETE FROM orderdetail
WHERE ctid IN (
	SELECT ctid
	FROM CTE
	WHERE rn > 1
);

-- After no more duplicates, we set (orderid, prod_id) for primary key of the table
ALTER TABLE orderdetail
ADD PRIMARY KEY (orderid, prod_id);

