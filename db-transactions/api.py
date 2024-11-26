import os
from dotenv import load_dotenv
from quart import Quart
import sqlalchemy as sql
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


load_dotenv()

# API URI
api_port = os.getenv('API_SERVER_PORT')
api_uri = 'http://127.0.0.1:' + api_port

# Quart app and SQLAlchemy connection
app = Quart(__name__)
engine = create_async_engine(os.getenv('DATABASE_URI'), execution_options={"autocommit":False})
AsyncSessionLocal = sql.orm.sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False)

# borraCiudad parameters
incorrect_order = False
intermediate_commit = False


@app.route('/borraCiudad/<str:city>', methods=['DELETE'])
async def delete_city_users(city: str) -> None:
    """
    Deletes all the users from a given city, and the information asociated
    to them.

    Method:
    -------
    DELETE
    """
    
    if incorrect_order:
        borraCiudad_wrong_order(city)
    elif intermediate_commit:
        borraCiudad_intermediate_commit(city)
    else:
        borraCiudad(city)

    return


def borraCiudad(city: str) -> None:
    """
    Correct way to delete all the users from a given city and the information
    asociated to them.
    """


if __name__ == '__main__':
    app.run(host='api_db', port=int(api_port))