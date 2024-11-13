import os
from quart import Quart, request, jsonify
from dotenv import load_dotenv
import sqlalchemy as sql
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from datetime import datetime

app = Quart(__name__)
load_dotenv()

engine = create_async_engine(os.getenv('DATABASE_URL'), echo=True)
AsyncSessionLocal = sql.orm.sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@app.route('/register', methods=['PUT'])
async def register():
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
        return jsonify({"message": "There is something wrong with the request"}), 400

    try:
        async with AsyncSessionLocal() as session:
            # Add new customer to the system
            await session.execute(
                sql.text("""
                    INSERT INTO customers (address, email, creditcard, username, password)
                    VALUES (:address, :email, :creditcard, :username, :password)
                """),
                {
                    'address': address,
                    'email': email,
                    'creditcard': creditcard,
                    'username': username,
                    'password': password
                }
            )

            await session.commit()
            return jsonify({"message": "User registered successfully"}), 201
        
    except sql.IntegrityError as e:
        # Rollback the session in case of error
        await session.rollback()

        if "unique constraint" in str(e.orig):
            return jsonify({"error": "User already exists"}), 400
        else:
            return jsonify({"error": "Database error during registration"}), 500

    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
        

@app.route('/login', methods=['POST'])
async def login():
    data = await request.get_json()

    try:
        email = data.get('email')
        password = data.get('password')
    except KeyError as e:
        return jsonify({"message": f"Missing field {str(e)}"}), 400
    except TypeError:
        return jsonify({"message": f"There is something wrong with the request."}), 400
    
    try:
        async with AsyncSessionLocal() as session:
            # Search for the customer in the system
            result = await session.execute(
                sql.text("SELECT * FROM customers WHERE email = :email"),
                {'email': email}
            )
            customer = result.fetchone()

        # Check if the customer credentials are valid
        if customer and hash(customer.password) == password:
            return jsonify({"customerid": customer.customerid, "message": "Login successful"}), 200
        else:
            return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    

@app.route('/delete/<customerid>', methods=['DELETE'])
async def delete_user(customerid):
    
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
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/balance/<customerid>', methods=['POST', 'PUT'])
async def add_balance(customerid):
    data = await request.get_json()

    try:
        amount = data.get('amount')
    except KeyError as e:
        return jsonify({"message": f"Missing field {str(e)}"}), 400
    except TypeError:
        return jsonify({"message": f"There is something wrong with the request"}), 400

    if amount <= 0:
        return jsonify({"message": "Amount must be greater than 0"}), 400

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                sql.text("UPDATE customers SET balance = balance + :amount WHERE customerid = :customerid"),
                {'amount': amount, 'customerid': customerid}
            )
            await session.commit()

            if result.rowcount == 0:
                return jsonify({"error": "User not found"}), 404
            
            return jsonify({"message": "Balance updated successfully"}), 200
        
    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/products', methods=['GET'])
async def get_products():
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                sql.text('''SELECT prod_id, movietitle, year, directorname, price, description, stock 
                            FROM products NATURAL JOIN imdb_movies 
                            NATURAL JOIN imdb_directormovies 
                            NATURAL JOIN imdb_directors
                            NATURAL JOIN inventory''')
            )
            products = [dict(row) for row in result.fetchall()]

            if not products:
                return jsonify({"error": "No products on database"}), 404
            
            return jsonify({"data": products}), 200
        
    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/order/customerid', methods=['PUT'])
async def create_order(customerid):
    try:
        orderdate = datetime.now().strftime('%Y-%m-%d')
        
        async with AsyncSessionLocal() as session:
            # Insert the new order and retrieve the generated orderid
            result = await session.execute(
                sql.text('''
                    INSERT INTO orders (customerid, orderdate)
                    VALUES (:customerid, :orderdate)
                    RETURNING orderid
                '''),
                {'customerid': customerid, 'orderdate': orderdate}
            )
            await session.commit()

            # Return the orderid in the response
            return jsonify({"orderid": result.scalar(), "message": "Order created successfully"}), 201
        
    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/orders/<customerid>', methods=['GET'])
async def get_customer_orders(customerid):
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                sql.text('''SELECT orderid, orderdate, totalamount, status
                            FROM orders
                            WHERE customerid = :customerid'''),
                {'customerid': customerid}
            )
            orders = [dict(row) for row in result.fetchall()]

            if not orders:
                return jsonify({"error": "No orders made by the customer yet."}), 404
            
            return jsonify({"data": orders}), 200
        
    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/order/<orderid>', methods=['GET'])
async def get_order_details(orderid):
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                sql.text('''SELECT orderid, orderdate, netamount, tax totalamount, status
                            FROM orders
                            WHERE orderid = :orderid'''),
                {'orderid': orderid}
            )
            order = result.fetchone()

            result = await session.execute(
                sql.text('''SELECT p.prod_id, movietitle, year, directorname, p.price, quantity, description, stock 
                            FROM products as p
                            NATURAL JOIN imdb_movies 
                            NATURAL JOIN imdb_directormovies 
                            NATURAL JOIN imdb_directors
                            NATURAL JOIN inventory
                            INNER JOIN orderdetail AS o ON o.prod_id = p.prod_id
                            WHERE o.orderid = :orderid'''),
                {'orderid': orderid}
            )

            products = [dict(row) for row in result.fetchall()]

            if not products:            
                return jsonify({"data": order}), 200
            else:
                return jsonify({"data": {"order": order, "products": products}}), 200
        
    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    

@app.route('/order/<orderid>', methods=['DELETE'])
async def delete_order(orderid):
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                sql.text('''DELETE FROM orders
                            WHERE orderid = :orderid'''),
                {'orderid': orderid}
            )

            if result.rowcount == 0:
                return jsonify({"error": "User not found"}), 404
            
            return jsonify({"message": "Order removed successfully"}), 200

    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    

@app.route('/order/<orderid>/products', methods=['PUT', 'POST'])
async def add_product(orderid):
    data = await request.get_json()

    try:
        prod_id = data.get('prod_id')
        quantity = data.get('quantity')
    except KeyError as e:
        return jsonify({"message": f"Missing field {str(e)}"}), 400
    except TypeError:
        return jsonify({"message": f"There is something wrong with the request"}), 400
    
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

            return jsonify({"message": "Product added to order successfully"}), 200
                        
    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/order/<orderid>/products', methods=['DELETE'])
async def remove_product(orderid):
    data = await request.get_json()

    try:
        prod_id = data.get('prod_id')
        quantity = data.get('quantity')
    except KeyError as e:
        return jsonify({"message": f"Missing field {str(e)}"}), 400
    except TypeError:
        return jsonify({"message": f"There is something wrong with the request"}), 400

    if quantity <= 0:
        return jsonify({"message": f"Cannot remove zero or less products"}), 400

    try:
        async with AsyncSessionLocal() as session:
            # Check if the order exists
            result = await session.execute(
                sql.text("SELECT * FROM orders WHERE orderid = :orderid"),
                {'orderid': orderid}
            )

            if result.rowcount == 0:
                return jsonify({"error": "Order not found"}), 404

            # Check if the product exists in the order and retrieve the current quantity
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
                return jsonify({"error": "Not enough product quantity to remove"}), 400

            # Update the quantity in the orderdetail table by subtracting the given quantity
            if current_quantity == quantity:
                # If the quantity to be removed is equal to the current quantity, delete the product entry
                await session.execute(
                    sql.text("""
                        DELETE FROM orderdetail
                        WHERE orderid = :orderid AND prod_id = :prod_id
                    """),
                    {'orderid': orderid, 'prod_id': prod_id}
                )
            else:
                # If the quantity to be removed is less than the current quantity, just update the quantity
                await session.execute(
                    sql.text("""
                        UPDATE orderdetail
                        SET quantity = quantity - :quantity
                        WHERE orderid = :orderid AND prod_id = :prod_id
                    """),
                    {'orderid': orderid, 'prod_id': prod_id, 'quantity': quantity}
                )

            # Commit the changes
            await session.commit()

            return jsonify({"message": "Product quantity removed from order successfully"}), 200
    
    except Exception as e:
        # Rollback the session in case of an unexpected error
        await session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/order/<orderid>/pay', methods=['PUT'])
async def pay_order(orderid):
    try:
        # Retrieve the order status
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                sql.text("""
                    SELECT status FROM orders WHERE orderid = :orderid
                """),
                {'orderid': orderid}
            )

            if result.rowcount == 0:
                return jsonify({"error": "Order not found"}), 404

            order_status = result.scalar()

            # Check if the order status is 'Processed'
            if order_status != 'Processed':
                return jsonify({"error": "Order cannot be paid because it is not 'Processed'"}), 400

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

    except sql.SQLAlchemyError as e:
        await session.rollback()

        # Check for the specific database error or notice
        if 'NOTICE' in str(e.orig):
            return jsonify({"error": f"Error: {str(e.orig)}"}), 400
        else:
            return jsonify({"error": f"Error: {str(e)}"}), 500

    except Exception as e:
        # Handle unexpected errors
        await session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    

if __name__ == "__main__":
    app.run(host='localhost', port=int(os.getenv('API_SERVER_PORT')))
    # app.run(host="api_db", port=int(os.getenv('API_SERVER_PORT')))
