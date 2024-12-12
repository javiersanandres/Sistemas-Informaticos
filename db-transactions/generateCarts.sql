DO $$
DECLARE
    selected_customers RECORD;
BEGIN
    -- Seleccionar 5 clientes de ciudades distintas
    FOR selected_customers IN 
        SELECT DISTINCT ON (city) customerid, city 
        FROM customers 
        WHERE city IS NOT NULL 
        LIMIT 5
    LOOP
        -- Actualizar el status de un pedido de cada cliente seleccionado
        UPDATE orders
        SET status = NULL
        WHERE orderid = (
            SELECT orderid 
            FROM orders 
            WHERE customerid = selected_customers.customerid
              AND status IS NOT NULL
            LIMIT 1
        );

        -- Mostrar el customerid en la consola
        RAISE NOTICE 'Customer ID: %, City: %', selected_customers.customerid, selected_customers.city;
    END LOOP;
END $$;