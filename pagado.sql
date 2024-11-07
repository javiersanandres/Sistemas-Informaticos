-- First, create the trigger function
CREATE OR REPLACE FUNCTION pagado_tr_function()
RETURNS TRIGGER AS $$
DECLARE
	order_prod record;
	customer_order record;
BEGIN
	-- Update inventory
	FOR order_prod IN (SELECT p.prod_id, quantity, stock, sales
						  FROM (orderdetail as o INNER JOIN (products as p NATURAL JOIN inventory) 
						  ON o.prod_id = p.prod_id) 
						  WHERE orderid = NEW.orderid)
	LOOP
		-- Check if the product is available in stock
		IF order_prod.stock - order_prod.quantity < 0 THEN
        	RAISE NOTICE 'Cannot pay order as there are products not available in stock';
			ROLLBACK; -- Undo all previous changes as the order is not being paid
			
			UPDATE orders 
			SET status = NULL -- Mark the order as unpaid
			WHERE orderid = NEW.orderid;
			
			RETURN NEW;
		ELSE
			UPDATE inventory
			SET stock = order_prod.stock - order_prod.quantity,
				sales = order_prod.sales + order_prod.quantity
			WHERE prod_id = order_prod.prod_id;
		END IF;
    END LOOP;

	-- Try to pay for the order
	CALL calculateOrderPrice(NEW.orderid); -- Calculate the price just in case
	
	SELECT customerid, balance, totalamount INTO customer_order
	FROM orders NATURAL JOIN customers 
	WHERE orderid = NEW.orderid;
	
	IF customer_order.balance - customer_order.totalamount < 0 THEN
		RAISE NOTICE 'Cannot pay order as there is not enough balance in account';
		ROLLBACK; -- Undo all previous changes as the order is not being paid
		
		UPDATE orders 
		SET status = NULL -- Mark the order as unpaid
		WHERE orderid = NEW.orderid; 
	ELSE
		UPDATE customers 
		SET balance = customer_order.balance - customer_order.totalamount
		WHERE customerid = customer_order.customerid;
	END IF;
	
	RETURN NEW;
END;
$$
LANGUAGE plpgsql;

-- Create the trigger for changes in orders table
CREATE OR REPLACE TRIGGER pagado
AFTER UPDATE ON orders
FOR EACH ROW
WHEN (NEW.status = 'Paid')
	EXECUTE FUNCTION pagado_tr_function();
