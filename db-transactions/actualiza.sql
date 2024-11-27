-- Delete ON DELETE CASCADE constraints
ALTER TABLE orders DROP CONSTRAINT orders_customerid_fkey;
ALTER TABLE orderdetail DROP CONSTRAINT orderdetail_orderid_fkey;

-- Add foreign keys without ON DELETE CASCADE constraint
ALTER TABLE orders ADD CONSTRAINT orders_customerid_fkey
FOREIGN KEY (customerid) REFERENCES customers(customerid);

ALTER TABLE orderdetail ADD CONSTRAINT orderdetail_orderid_fkey
FOREIGN KEY (orderid) REFERENCES orders(orderid);