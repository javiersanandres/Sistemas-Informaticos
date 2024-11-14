--- RESTRICTIONS AND CASCADE ACTIONS

-- Add cascade actions to already existing foreign keys in imdb_directormovies
ALTER TABLE imdb_directormovies
DROP CONSTRAINT imdb_directormovies_directorid_fkey,
DROP CONSTRAINT imdb_directormovies_movieid_fkey,
ADD CONSTRAINT imdb_directormovies_directorid_fkey FOREIGN KEY (directorid) REFERENCES imdb_directors(directorid) ON DELETE CASCADE ON UPDATE CASCADE,
ADD CONSTRAINT imdb_directormovies_movieid_fkey FOREIGN KEY (movieid) REFERENCES imdb_movies(movieid) ON DELETE CASCADE ON UPDATE CASCADE;

-- Add cascade actions to already existing foreign keys in imdb_moviecountries
ALTER TABLE imdb_moviecountries
DROP CONSTRAINT imdb_moviecountries_movieid_fkey,
ADD CONSTRAINT imdb_moviecountries_movieid_fkey FOREIGN KEY (movieid) REFERENCES imdb_movies(movieid) ON DELETE CASCADE ON UPDATE CASCADE;

-- Add cascade actions to already existing foreign keys in imdb_moviegenres
ALTER TABLE imdb_moviegenres
DROP CONSTRAINT imdb_moviegenres_movieid_fkey,
ADD CONSTRAINT imdb_moviegenres_movieid_fkey FOREIGN KEY (movieid) REFERENCES imdb_movies(movieid) ON DELETE CASCADE ON UPDATE CASCADE;

-- Add cascade actions to already existing foreign keys in imdb_movielanguages
ALTER TABLE imdb_movielanguages
DROP CONSTRAINT imdb_movielanguages_movieid_fkey,
ADD CONSTRAINT imdb_movielanguages_movieid_fkey FOREIGN KEY (movieid) REFERENCES imdb_movies(movieid) ON DELETE CASCADE ON UPDATE CASCADE;

-- Add cascade actions to already existing foreign keys in imdb_movielanguages
ALTER TABLE products
DROP CONSTRAINT products_movieid_fkey,
ADD CONSTRAINT products_movieid_fkey FOREIGN KEY (movieid) REFERENCES imdb_movies(movieid) ON DELETE CASCADE ON UPDATE CASCADE;

-- Add foreign keys to inventory table
ALTER TABLE inventory
ADD CONSTRAINT inventory_product_fkey FOREIGN KEY (prod_id) REFERENCES products(prod_id) ON DELETE CASCADE ON UPDATE CASCADE;

-- Add primary key and foreign keys to imdb_actormovies table
ALTER TABLE imdb_actormovies
ADD PRIMARY KEY (actorid, movieid, character),
ADD CONSTRAINT actormovies_actor_fkey FOREIGN KEY (actorid) REFERENCES imdb_actors(actorid) ON DELETE CASCADE ON UPDATE CASCADE,
ADD CONSTRAINT actormovies_movie_fkey FOREIGN KEY (movieid) REFERENCES imdb_movies(movieid) ON DELETE CASCADE ON UPDATE CASCADE;

-- Make email be non null and unique along the table
ALTER TABLE customers
ALTER COLUMN email SET NOT NULL,
ADD CONSTRAINT customers_email_unique UNIQUE (email);

-- Add foreign keys to orders table
ALTER TABLE orders
ALTER COLUMN netamount SET DEFAULT 0.00,
ALTER COLUMN totalamount SET DEFAULT 0.00,
ADD CONSTRAINT orders_customer_fkey FOREIGN KEY (customerid) REFERENCES customers(customerid) ON DELETE CASCADE ON UPDATE CASCADE;

-- Add foreign keys to orderdetail table and new primary key
ALTER TABLE orderdetail
-- Although we'd have added this in here, the multivalued and repeated rows
-- problem must be handled in another script called actualizaTablas.sql
-- ADD PRIMARY KEY (orderid, prod_id) -- will be fixed in another script
ADD CONSTRAINT orderdetail_order_fkey FOREIGN KEY (orderid) REFERENCES orders(orderid) ON DELETE CASCADE ON UPDATE CASCADE,
ADD CONSTRAINT orderdetail_product_fkey FOREIGN KEY (prod_id) REFERENCES products(prod_id) ON DELETE CASCADE ON UPDATE CASCADE;



--- ADDING NEW FUNCTIONALITY AS STATED IN PARAGRAPH A

-- Store the customers' balance in the database
ALTER TABLE customers
ADD COLUMN balance NUMERIC(10, 2) DEFAULT 0.00;


-- Create new table likes to store customers' valorations. We have assumed that
-- the customers rate specific products related to a movie.
CREATE TABLE likes (
    customerid INT NOT NULL,
    prod_id INT NOT NULL,
    like_value BOOLEAN NOT NULL, -- true for like, false for unlike
	review TEXT,
	PRIMARY KEY (customerid, prod_id), -- only one valoration per product for each user
    CONSTRAINT likes_customerid_fkey FOREIGN KEY (customerid) REFERENCES customers(customerid) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT likes_prod_id_fkey FOREIGN KEY (prod_id) REFERENCES products(prod_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Increase the number of characters in password field. Previous value was 50,
-- as there is no specification in the exercise statement, increased to 100
ALTER TABLE customers
ALTER COLUMN password TYPE VARCHAR(100);


-- Create function that gives away a random balance to each customer
CREATE OR REPLACE FUNCTION setCustomersBalance(IN initialBalance BIGINT)
RETURNS VOID AS $$
BEGIN
    UPDATE customers
    SET balance = ROUND((random() * initialBalance)::NUMERIC, 2);
END;
$$ LANGUAGE plpgsql;

-- Call previous function
SELECT setCustomersBalance(200);


