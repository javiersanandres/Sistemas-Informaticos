-- Apartado b
ALTER TABLE customers
    ADD COLUMN promo DECIMAL(5, 2) DEFAULT 0.00;

-- Apartado c y d
CREATE OR REPLACE FUNCTION update_promo_tr_function()
    RETURNS TRIGGER AS $$
BEGIN
    -- Actualizar los precios en orderdetail para los carritos (orders.status es NULL)
    UPDATE orderdetail
    SET price = products.price * (1 - NEW.promo / 100)  -- Aplicar el descuento al precio base
    FROM products, orders
    WHERE orderdetail.prod_id = products.prod_id
      AND orderdetail.orderid = orders.orderid
      AND orders.customerid = NEW.customerid
      AND orders.status IS NULL;

    -- Recalcular netamount y totalamount en la tabla orders
    UPDATE orders
    SET
        netamount = subquery.discounted_total,  -- Total sin impuestos
        totalamount = ROUND(subquery.discounted_total * (1 + COALESCE(orders.tax, 0) / 100.0), 2)  -- Total con impuestos
    FROM (
             SELECT od.orderid, SUM(od.price * od.quantity) AS discounted_total
             FROM orderdetail od
                      JOIN orders o ON od.orderid = o.orderid
             WHERE o.customerid = NEW.customerid AND o.status IS NULL
             GROUP BY od.orderid
         ) AS subquery
    WHERE orders.orderid = subquery.orderid;

    PERFORM pg_sleep(300); -- Introducir retardo

    -- Retornar el nuevo valor del cliente
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crear un trigger para aplicar la función cuando se actualice la columna 'promo' de un cliente
CREATE TRIGGER update_promo
    AFTER UPDATE OF promo
    ON customers
    FOR EACH ROW
    WHEN (OLD.promo IS DISTINCT FROM NEW.promo)  -- Solo cuando cambie el valor de 'promo'
EXECUTE FUNCTION update_promo_tr_function();