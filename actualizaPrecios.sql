-- First, we create a procedure which calculates the total price of an order
CREATE OR REPLACE PROCEDURE calculateOrderPrice(IN order_id INT)
LANGUAGE plpgsql
AS $$
DECLARE
    order_amount NUMERIC := 0;
BEGIN
	-- Calculate the sum and store it in a variable
	SELECT COALESCE(SUM(quantity * p.price), 0) INTO order_amount
		FROM (orderdetail as o INNER JOIN products as p ON o.prod_id = p.prod_id) 
		WHERE orderid = order_id;
    
    -- Update orders table with the calculated total for that order
    UPDATE orders
    SET totalamount = order_amount
    WHERE orderid = order_id;
END;
$$;


-- Second, we create another procedure which completes the order price in every order
CREATE OR REPLACE PROCEDURE calculateAllOrdersPrice()
LANGUAGE plpgsql
AS $$
DECLARE
    current_order INT;
BEGIN
	FOR current_order IN (SELECT orderid FROM orders) 
	LOOP
        CALL calculateOrderPrice(current_order);
    END LOOP;
END;
$$;

-- Call the method to complete totalamount field for each order
CALL calculateAllOrdersPrice()