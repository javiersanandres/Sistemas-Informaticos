import os
from quart import Quart, request, jsonify
from dotenv import load_dotenv
import sqlalchemy as sql
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from datetime import datetime

app = Quart(__name__)
load_dotenv()

engine = create_async_engine(os.getenv('DATABASE_URL'), echo=True)
AsyncSessionLocal = sql.orm.sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False)


@app.route('/register', methods=['PUT'])
async def register():
    """
    Registers a new user in the system.

    This endpoint handles user registration by collecting user information
    (username, password, address, credit card, email) and adding the details
    to the `customers` table in the database.

    Method:
    -------
    PUT
    """

    data = await request.get_json()
    try:
        username = data.get('username')
        password = data.get('password')
        address = data.get('address')
        creditcard = data.get('creditcard')
        email = data.get('email')
    except KeyError as e:
        return jsonify({"message": f"Missing field {str(e)}"}), 400
    except TypeError:
        return jsonify(
            {"message": "There is something wrong with the request"}), 400

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                sql.text("""
                SELECT MAX(customerid) FROM customers
                """))

            customerid = result.scalar() + 1

            # Add new customer to the system
            await session.execute(
                sql.text("""
                    INSERT INTO customers (customerid, address, email,
                                            creditcard, username, password)
                    VALUES (:customerid, :address, :email,
                            :creditcard, :username, :password)
                """),
                {
                    'customerid': customerid,
                    'address': address,
                    'email': email,
                    'creditcard': creditcard,
                    'username': username,
                    'password': password
                }
            )

            await session.commit()
            return jsonify({"message": "User registered successfully"}), 201
    except sql.exc.IntegrityError as e:
        # Rollback the session in case of error
        await session.rollback()

        # Error caused because user already exists
        if "unique constraint" in str(e.orig):
            return jsonify({"error": "User already exists"}), 400

        return jsonify({"error": "Database error during registration"}), 500
    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify(
            {"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/login', methods=['POST'])
async def login():
    """
    Authenticates a user by verifying their email and password.

    This endpoint handles user login by retrieving and validating
    user credentials (email and password) from the `customers`
    table in the database.

    Method:
    -------
    POST
    """

    data = await request.get_json()

    try:
        email = data.get('email')
        password = data.get('password')
    except KeyError as e:
        return jsonify({"message": f"Missing field {str(e)}"}), 400
    except TypeError:
        return jsonify(
            {"message": f"There is something wrong with the request."}), 400

    try:
        async with AsyncSessionLocal() as session:
            # Search for the customer in the system
            result = await session.execute(
                sql.text("SELECT * FROM customers WHERE email = :email"),
                {'email': email}
            )
            customer = result.fetchone()

        # Check if the customer credentials are valid
        if customer and password == customer.password:
            return jsonify({"customerid": customer.customerid,
                           "message": "Login successful"}), 200

        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify(
            {"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/<int:customerid>', methods=['DELETE'])
async def delete_user(customerid):
    """
    Deletes a user by customer ID.

    This endpoint handles user deletion by removing the user with the specified
    `customerid` from the `customers` table in the database.

    Method:
    -------
    DELETE
    """

    try:
        async with AsyncSessionLocal() as session:
            # Query the deletion of that user
            result = await session.execute(
                sql.text("""
                    DELETE FROM customers WHERE customerid = :customerid
                    """),
                {'customerid': customerid}
            )
            await session.commit()

            if result.rowcount == 0:
                return jsonify({"error": "User not found"}), 404

            return jsonify({"message": "User deleted successfully"}), 200

    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify(
            {"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/<int:customerid>', methods=['GET'])
async def get_user_details(customerid):
    """
    Retrieves details of a user by customer ID.

    This endpoint handles fetching user details (address, email, credit card,
    username, password, and balance) for the specified `customerid` from the
    `customers` table in the database.

    Method:
    -------
    GET
    """

    try:
        async with AsyncSessionLocal() as session:
            # Query the deletion of that user
            result = await session.execute(
                sql.text("""
                    SELECT address, email, creditcard, username,
                            password, balance
                    FROM customers
                    WHERE customerid = :customerid
                    """),
                {'customerid': customerid}
            )

            # Unknown user
            if result.rowcount == 0:
                return jsonify({"error": "User not found"}), 404

            return jsonify({"data": dict(result.mappings().first())}), 200

    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify(
            {"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/balance/<int:customerid>', methods=['POST', 'PUT'])
async def add_balance(customerid):
    """
    Adds a specified amount to a user's balance by customer ID.

    This endpoint updates the balance for the user with the given `customerid`,
    increasing it by the specified `amount` provided in the request data.

    Methods:
    --------
    POST, PUT
    """

    data = await request.get_json()

    try:
        amount = round(float(data.get('amount')), 2)
    except KeyError as e:
        return jsonify({"message": f"Missing field {str(e)}"}), 400
    except TypeError:
        return jsonify(
            {"message": f"There is something wrong with the request"}), 400

    if amount <= 0:
        return jsonify({"message": "Amount must be greater than 0"}), 400

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                sql.text("""UPDATE customers SET balance = balance + :amount
                            WHERE customerid = :customerid"""),
                {'amount': amount, 'customerid': customerid}
            )
            await session.commit()

            if result.rowcount == 0:
                return jsonify({"error": "User not found"}), 404

            return jsonify({"message": "Balance updated successfully"}), 200

    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify(
            {"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/products', methods=['GET'])
async def get_products():
    """
    Retrieves a list of available products.

    This endpoint fetches product details, including ID, movie title, year,
    director name, price, description, and stock, by querying multiple tables
    related to products and inventory.

    Method:
    -------
    GET
    """

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                sql.text("""SELECT prod_id, movietitle, year, directorname,
                                    price, description, stock
                            FROM products NATURAL JOIN imdb_movies
                            NATURAL JOIN imdb_directormovies
                            NATURAL JOIN imdb_directors
                            NATURAL JOIN inventory""")
            )
            if result.rowcount == 0:
                return jsonify({"error": "No products on database"}), 404

            products = [dict(row) for row in result.mappings().all()]

            return jsonify({"data": products}), 200
    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify(
            {"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/products/<int:prod_id>', methods=['GET'])
async def get_products_details(prod_id):
    """
    Retrieves details of a specific product by product ID.

    This endpoint fetches detailed information for a product with the specified
    `prod_id`, including movie title, year, director name, price, description,
    and stock.

    Method:
    -------
    GET
    """

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                sql.text("""SELECT prod_id, movietitle, year, directorname,
                                    price, description, stock
                            FROM products NATURAL JOIN imdb_movies
                            NATURAL JOIN imdb_directormovies
                            NATURAL JOIN imdb_directors
                            NATURAL JOIN inventory
                            WHERE prod_id = :prod_id"""),
                {'prod_id': prod_id}
            )

            # Unknown product
            if result.rowcount == 0:
                return jsonify({"error": "No such product on database"}), 404

            return jsonify({"data": dict(result.mappings().first())}), 200
    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify(
            {"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/order/<int:customerid>', methods=['PUT'])
async def create_order(customerid):
    """
    Creates a new order for a specified customer.

    This endpoint creates a new order for the customer with the specified
    `customerid`, generating a new `orderid` and storing the order date.

    Method:
    -------
    PUT
    """

    try:
        orderdate = datetime.now()

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                sql.text("""
                    SELECT MAX(orderid) FROM orders
                """))

            orderid = result.scalar() + 1

            # Insert the new order and retrieve the generated orderid
            await session.execute(
                sql.text("""
                    INSERT INTO orders (orderid, customerid, orderdate)
                    VALUES (:orderid, :customerid, :orderdate)
                """),
                {'orderid': orderid, 'customerid': customerid,
                 'orderdate': orderdate}
            )
            await session.commit()

            # Return the orderid in the response
            return jsonify(
                {"orderid": orderid,
                 "message": "Order created successfully"}), 201
    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify(
            {"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/orders/<int:customerid>', methods=['GET'])
async def get_customer_orders(customerid):
    """
    Retrieves all orders for a specific customer.

    This endpoint fetches a list of orders made by the customer with the
    specified `customerid`, including order ID, date, total amount, and status.

    Method:
    -------
    GET
    """

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                sql.text("""SELECT orderid, orderdate, totalamount, status
                            FROM orders
                            WHERE customerid = :customerid"""),
                {'customerid': customerid}
            )

            if result.rowcount == 0:
                return jsonify(
                    {"error": "No orders made by the customer yet."}), 404

            orders = [dict(row) for row in result.mappings().all()]
            return jsonify({"data": orders}), 200
    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify(
            {"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/order/<int:orderid>', methods=['GET'])
async def get_order_details(orderid):
    """
    Retrieves details of a specific order by order ID.

    This endpoint fetches details of an order, including order ID, date,
    net amount, tax, total amount, and status, for the specified `orderid`.
    It also retrieves the list of products associated with the order.

    Method:
    -------
    GET
    """

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                sql.text("""SELECT orderid, orderdate, netamount, tax,
                            totalamount, status
                            FROM orders
                            WHERE orderid = :orderid"""),
                {'orderid': orderid}
            )

            if result.rowcount == 0:
                return jsonify({"error": "No orders with that id."}), 404

            order = dict(result.mappings().first())
            result = await session.execute(
                sql.text("""SELECT p.prod_id, movietitle, year, directorname,
                                    p.price, quantity, description, stock
                                FROM products as p
                                NATURAL JOIN imdb_movies
                                NATURAL JOIN imdb_directormovies
                                NATURAL JOIN imdb_directors
                                NATURAL JOIN inventory
                                INNER JOIN orderdetail AS o
                                        ON o.prod_id = p.prod_id
                                WHERE o.orderid = :orderid"""),
                {'orderid': orderid}
            )

            if result.rowcount == 0:
                return jsonify({"data": order}), 200

            products = [dict(row) for row in result.mappings().all()]
            return jsonify(
                {"data": {"order": order, "products": products}}), 200
    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify(
            {"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/order/<int:orderid>', methods=['DELETE'])
async def delete_order(orderid):
    """
    Deletes a specific order by order ID.

    This endpoint removes the order with the
    specified `orderid` from the database.

    Method:
    -------
    DELETE
    """

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                sql.text("""DELETE FROM orders
                            WHERE orderid = :orderid"""),
                {'orderid': orderid}
            )
            await session.commit()

            if result.rowcount == 0:
                return jsonify({"error": "User not found"}), 404

            return jsonify({"message": "Order removed successfully"}), 200
    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify(
            {"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/order/<int:orderid>/products', methods=['PUT', 'POST'])
async def add_product(orderid):
    """
    Adds a product to an order.

    This endpoint adds a product to the order with the specified `orderid`.
    If the product already exists in the order, it updates the quantity;
    otherwise, it inserts the new product into the order.

    Method:
    -------
    PUT, POST
    """

    data = await request.get_json()

    try:
        prod_id = int(data.get('prod_id'))
        quantity = int(data.get('quantity'))
    except KeyError as e:
        return jsonify({"message": f"Missing field {str(e)}"}), 400
    except TypeError:
        return jsonify(
            {"message": f"There is something wrong with the request"}), 400

    if quantity <= 0:
        return jsonify({"message": f"Cannot add zero or less products"}), 400

    try:
        async with AsyncSessionLocal() as session:
            # Find or create a cart order
            result = await session.execute(
                sql.text("SELECT * FROM orders WHERE orderid = :orderid"),
                {'orderid': orderid}
            )

            if result.rowcount == 0:
                return jsonify({"error": "Order not found"}), 404

            await session.execute(
                sql.text("""
                    INSERT INTO orderdetail (orderid, prod_id, quantity)
                    VALUES (:orderid, :prod_id, :quantity)
                    ON CONFLICT (orderid, prod_id)
                    DO UPDATE SET quantity = orderdetail.quantity + :quantity
                """),
                {'orderid': orderid, 'prod_id': prod_id, 'quantity': quantity}
            )

            await session.commit()

            return jsonify(
                {"message": "Product added to order successfully"}), 200
    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify(
            {"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/order/<int:orderid>/products', methods=['DELETE'])
async def remove_product(orderid):
    """
    Removes a product from an order.

    This endpoint removes a specified quantity of a product from the order with
    the given `orderid`. If the product quantity in the order is equal to the
    requested quantity, the product is removed completely. If the requested
    quantity is less than the existing quantity, it is subtracted.

    Method:
    -------
    DELETE
    """

    data = await request.get_json()

    try:
        prod_id = int(data.get('prod_id'))
        quantity = int(data.get('quantity'))
    except KeyError as e:
        return jsonify({"message": f"Missing field {str(e)}"}), 400
    except TypeError:
        return jsonify(
            {"message": f"There is something wrong with the request"}), 400

    if quantity <= 0:
        return jsonify(
            {"message": f"Cannot remove zero or less products"}), 400

    try:
        async with AsyncSessionLocal() as session:
            # Check if the order exists
            result = await session.execute(
                sql.text("SELECT * FROM orders WHERE orderid = :orderid"),
                {'orderid': orderid}
            )

            if result.rowcount == 0:
                return jsonify({"error": "Order not found"}), 404

            # Check if the product exists in the order and retrieve the current
            # quantity
            result = await session.execute(
                sql.text("""
                    SELECT quantity FROM orderdetail
                    WHERE orderid = :orderid AND prod_id = :prod_id
                """),
                {'orderid': orderid, 'prod_id': prod_id}
            )

            if result.rowcount == 0:
                return jsonify({"error": "Product not found in order"}), 404

            current_quantity = result.scalar()

            if current_quantity < quantity:
                return jsonify(
                    {"error": "Not enough product quantity to remove"}), 400

            # Update the quantity in the orderdetail table by subtracting the
            # given quantity
            if current_quantity == quantity:
                # If the quantity to be removed is equal to the current
                # quantity, delete the product entry
                await session.execute(
                    sql.text("""
                        DELETE FROM orderdetail
                        WHERE orderid = :orderid AND prod_id = :prod_id
                    """),
                    {'orderid': orderid, 'prod_id': prod_id}
                )
            else:
                # If the quantity to be removed is less than the current
                # quantity, just update the quantity
                await session.execute(
                    sql.text("""
                        UPDATE orderdetail
                        SET quantity = quantity - :quantity
                        WHERE orderid = :orderid AND prod_id = :prod_id
                    """),
                    {'orderid': orderid, 'prod_id': prod_id,
                     'quantity': quantity}
                )

            # Commit the changes
            await session.commit()

            return jsonify(
                {"message": "Product quantity removed from" +
                            "order successfully"}), 200
    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify(
            {"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/order/<int:orderid>/pay', methods=['POST'])
async def pay_order(orderid):
    """
    Pays for an order by updating its status to 'Paid'.

    This endpoint allows the user to pay for the order with the specified
    `orderid`. The order must be in a 'Processed' state to be paid. If the
    order status is not 'Processed', it returns an error indicating that the
    order cannot be paid.

    Method:
    -------
    POST
    """

    try:
        # Retrieve the order status
        async with AsyncSessionLocal() as session:
            # Update the order status to 'Paid', due to previously made
            # trigger all possible failures have already been considered
            await session.execute(
                sql.text("""
                    UPDATE orders
                    SET status = 'Paid'
                    WHERE orderid = :orderid
                """),
                {'orderid': orderid}
            )

            # Commit the transaction
            await session.commit()

            return jsonify({"message": "Order successfully paid"}), 200
    except sql.exc.SQLAlchemyError as e:
        await session.rollback()

        error_message = str(e.orig).split(
            ":")[-1].strip()  # Get the actual error message
        return jsonify({"error": error_message}), 400
    except Exception as e:
        # Handle unexpected errors
        await session.rollback()
        return jsonify(
            {"error": f"An unexpected error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="api_db", port=int(os.getenv('API_SERVER_PORT')))
