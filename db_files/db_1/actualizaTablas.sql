-- Remove duplicates from orderdetail table
DO $$
BEGIN
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
      AND od.prod_id = sq.prod_id
      AND od.ctid = (
          SELECT MIN(ctid)
          FROM orderdetail
          WHERE orderid = sq.orderid AND prod_id = sq.prod_id
      );

    -- Delete the duplicate rows, keeping only the row with the minimum ctid
	-- and the one reflecting the actual quantity for each product and order
    DELETE FROM orderdetail
    WHERE ctid NOT IN (
        SELECT MIN(ctid)
        FROM orderdetail
        GROUP BY orderid, prod_id
    );
END $$;

-- After no more duplicates, we set (orderid, prod_id) for primary key of the table
ALTER TABLE orderdetail
ADD PRIMARY KEY (orderid, prod_id);



