-- First, create the trigger function
CREATE OR REPLACE FUNCTION actualizaCarrito_tr_function()
RETURNS TRIGGER AS $$
BEGIN
	IF new.orderid IS NOT NULL THEN -- NOT NULL when UPDATE OR INSERT
		CALL calculateOrderPrice(new.orderid);
	ELSIF old.orderid IS NOT NULL THEN -- NOT NULL when DELETE
		CALL calculateOrderPrice(old.orderid);
	END IF;
    RETURN NEW;
END;
$$
LANGUAGE plpgsql;

-- Create the trigger for changes in orders table
CREATE OR REPLACE TRIGGER actualizaCarrito
AFTER INSERT OR DELETE OR UPDATE ON orderdetail
FOR EACH ROW EXECUTE
FUNCTION actualizaCarrito_tr_function();