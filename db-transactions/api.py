from typing import Any, List
import os
from dotenv import load_dotenv
from quart import Quart, jsonify, request
import sqlalchemy as sql
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.exc import SQLAlchemyError


load_dotenv()

# API URI
api_port = os.getenv('API_SERVER_PORT')
api_uri = 'http://127.0.0.1:' + api_port

# Quart app and SQLAlchemy connection
app = Quart(__name__)
engine = create_async_engine(os.getenv('DATABASE_URI'), execution_options={'autocommit': False})
AsyncSessionLocal = sql.orm.sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False)


@app.route('/borraCiudad/<city>', methods=['DELETE'])
async def delete_city_users(city: str) -> Any:
    """
    Deletes all the users from a given city, and the information asociated
    to them.

    Method:
    -------
    DELETE
    """

    # Parse parameters that control the execution flow
    data = await request.get_json()
    try:
        wrong_order = data.get('wrong_order', False)
        progressive = data.get('progressive', False)
    except KeyError as e:
        return jsonify({'message': f'Missing field {str(e)}'}), 400
    except TypeError:
        return jsonify(
            {'message': 'There is something wrong with the request'}), 400
    
    if wrong_order:
        if progressive:
            print('[API] Deleting users in wrong order with intermediate commits...')
        else:
            print('[API] Deleting users in wrong order...')
        response = await borraCiudad_wrong_order(city, progressive=progressive)
    else:
        print('[API] Deleting users the correct way...')
        response = await borraCiudad(city)

    return response


async def borraCiudad(city: str) -> Any:
    """
    Correct way to delete all the users from a given city and the information
    asociated to them.
    """
    session = AsyncSessionLocal()

    try:
        await session.execute(sql.text('BEGIN'))
        
        # Get customers to be deleted from the database
        customers_to_delete = await get_city_customers(session, city)

        print(f'[API] Found {len(customers_to_delete)} customers to be deleted from the database.\n' \
              '[API] Starting with the deletion of the requested customers...')

        if not customers_to_delete:
            return jsonify({'message': f'Users from {city} successfully deleted from the database'}), 200
        
        # Get the orders made by the customers that will be deleted
        orders_to_delete = await get_orders_from_customers(session, customers_to_delete)

        # First, delete the order details
        await delete_orderdetails(session, orders_to_delete)
        print('[API] Order details associated to the users successfully deleted.')

        # Then, delete the orders made by the customers
        await delete_orders(session, orders_to_delete)
        print('[API] Orders associated to the users successfully deleted.')
        
        # Finally, delete the customers
        await delete_customers(session, customers_to_delete)
        print(f'[API] Users from {city} successfully deleted.')

        await session.commit()
        return jsonify({'message': f'Users from {city} successfully deleted from the database'}), 200

    except SQLAlchemyError as e:
        print('[API] An error occurred while deleting the users info from the database: ' + str(e))
        print('[API] Executing rollback...')

        # Rollback in case of error
        await session.rollback()
        return jsonify({'error': 'An error occurred: ' + str(e)}), 500
    
    finally:
        await session.close()


async def borraCiudad_wrong_order(city: str, progressive: bool = False) -> Any:
    """
    Deletes all the users from a given city and the information asociated
    to them in the wrong order, causing a rollback to happen.

    The parameter 'progressive' forces intermediate commits to happen.
    """
    session = AsyncSessionLocal()

    try:
        await session.execute(sql.text('BEGIN'))

        # Get customers to be deleted from the database
        customers_to_delete = await get_city_customers(session, city)
        
        print(f'[API] Found {len(customers_to_delete)} customers to be deleted from the database.\n' \
              '[API] Starting with the deletion of the requested customers...')

        if not customers_to_delete:
            return jsonify({'message': f'Users from {city} successfully deleted from the database'}), 200
        
        # Get the orders made by the customers that will be deleted
        orders_to_delete = await get_orders_from_customers(session, customers_to_delete)

        # First, delete the order details
        await delete_orderdetails(session, orders_to_delete)
        print('[API] Order details associated to the users successfully deleted.')

        if progressive:
            # Intermediate commit
            await session.commit()
            print('[API] Intermediate commit completed. Changes so far are persisted.')

            # Beginning new transaction
            await session.execute(sql.text('BEGIN'))
            print('[API] New transaction started after intermediate commit.')

        # Delete the customers (incorrect, should be done after deleting the orders)
        await delete_customers(session, customers_to_delete)
        print(f'[API] Users from {city} successfully deleted.')

        # Try deleting the orders (will cause a foreign key constraint failure)
        await delete_orders(session, orders_to_delete)
        print('[API] Orders associated to the users successfully deleted.')

        # The result won't be committed to the database
        await session.commit()
        return jsonify({'message': f'Users from {city} successfully deleted from the database'}), 200

    except SQLAlchemyError as e:
        print('[API] An error occurred while deleting the users info from the database: ' + str(e))
        print('[API] Executing rollback...')
        
        # Rollback in case of error
        await session.rollback()
        return jsonify({'error': 'An error occurred: ' + str(e)}), 500
    
    finally:
        await session.close()


async def get_city_customers(session: Any, city: str) -> List:
    """
    Gets the customers from a given city.
    """
    results = await session.execute(
                sql.text('SELECT c.customerid FROM customers c WHERE c.city = :city'),
                {'city': city}
            )
    
    return [row['customerid'] for row in results.mappings()]


async def get_orders_from_customers(session: Any, customer_ids: List) -> List:
    """
    Gets the orders made by the given customers.
    """
    results = await session.execute(
                sql.text('SELECT o.orderid FROM orders o WHERE o.customerid = ANY(:customer_ids)'),
                {'customer_ids': customer_ids}
            )
    
    return [row['orderid'] for row in results.mappings()]


async def delete_orderdetails(session: Any, order_ids: List) -> None:
    """
    Deletes the orderdetails associated to the given orders from the database.
    """
    try:
        await session.execute(
            sql.text('DELETE FROM orderdetail WHERE orderid = ANY(:order_ids)'),
            {'order_ids': order_ids}
        )
    
    except SQLAlchemyError as e:
        raise e


async def delete_orders(session: Any, order_ids: List) -> None:
    """
    Deletes the given orders from the database.
    """
    try:
        await session.execute(
            sql.text('DELETE FROM orders WHERE orderid = ANY(:order_ids)'),
            {'order_ids': order_ids}
        )
    
    except SQLAlchemyError as e:
        raise e


async def delete_customers(session: Any, customer_ids: List) -> None:
    """
    Deletes the given customers from the database.
    """
    try:
        await session.execute(
            sql.text('DELETE FROM customers WHERE customerid = ANY(:customer_ids)'),
            {'customer_ids': customer_ids}
        )
    
    except SQLAlchemyError as e:
        raise e


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(api_port))