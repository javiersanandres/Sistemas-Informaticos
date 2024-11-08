-- First, we create a procedure which calculates the total price of an order
-- We should note that this procedure is not meant to be used to update all
-- orders as it would be extremelly ineficient to make a join per call.
-- This code is meant to be used in the following exercises where only one
-- call is needed.
CREATE OR REPLACE PROCEDURE calculateOrderPrice(IN order_id INT, OUT order_amount NUMERIC)
LANGUAGE plpgsql
AS $$
BEGIN
	-- Calculate the sum and store it in a variable
	SELECT COALESCE(SUM(quantity * p.price), 0) INTO order_amount
	FROM orderdetail AS o
	INNER JOIN products AS p ON o.prod_id = p.prod_id
	WHERE o.orderid = order_id;
END;
$$;



CREATE OR REPLACE PROCEDURE updateOrderPrice(IN order_id INT)
LANGUAGE plpgsql
AS $$
DECLARE
	order_amount NUMERIC;
BEGIN
	-- Calculate the total and store it in order_amount
	CALL calculateOrderPrice(order_id, order_amount);
	UPDATE orders
	SET totalamount = order_amount
	WHERE orderid = order_id;
END;
$$;



-- We create the procedure which calculates and
-- completes the order price for every order.
CREATE OR REPLACE PROCEDURE updateAllOrdersPrice()
LANGUAGE plpgsql
AS $$
DECLARE
    current_order record;
BEGIN
	FOR current_order IN (SELECT orderid, SUM(COALESCE(quantity * p.price, 0)) as total
		FROM (orderdetail o INNER JOIN products p ON o.prod_id = p.prod_id) 
		GROUP BY orderid)
	LOOP
		UPDATE orders
		SET totalamount = current_order.total
		WHERE orderid = current_order.orderid;
	END LOOP;
END;
$$;

-- Call the method to complete totalamount field for each order
CALL updateAllOrdersPrice()