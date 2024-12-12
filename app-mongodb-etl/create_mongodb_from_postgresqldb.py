from sqlalchemy import create_engine, MetaData, select, func, and_
from pymongo import MongoClient

# Connections configuration
POSTGRESQL_URL = "postgresql://alumnodb:1234@localhost:5005/si1"
MONGODB_URL = "mongodb://localhost:27017/"
MONGO_DB_NAME = "si1"
MONGO_COLLECTION_NAME = "france"

# PostgreSQL connections
engine = create_engine(POSTGRESQL_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

# Database tables
movies_table = metadata.tables['imdb_movies']
genres_table = metadata.tables['imdb_moviegenres']
countries_table = metadata.tables['imdb_moviecountries']
actors_info_table = metadata.tables['imdb_actormovies']
directors_info_table = metadata.tables['imdb_directormovies']
actors_table = metadata.tables['imdb_actors']
directors_table = metadata.tables['imdb_directors']

# MongoDB connection
client = MongoClient(MONGODB_URL)
mongo_db = client[MONGO_DB_NAME]
mongo_collection = mongo_db[MONGO_COLLECTION_NAME]


def get_french_movies(conn):
    """
    Gets all French movies or all in which France has collaborated
    """
    query = (
        select(
            movies_table.c.movieid,
            movies_table.c.movietitle,
            movies_table.c.year) .join(
            countries_table,
            movies_table.c.movieid == countries_table.c.movieid) .where(
                countries_table.c.country == 'France'))
    return conn.execute(query).fetchall()


def get_related_movies(conn, movie_id, genres, most_related=True):
    """
    Gets related movies based on genres coincidences
    """

    # Common query components
    base_query = (
        select(
            movies_table.c.movietitle,
            movies_table.c.year
        )
        .select_from(
            genres_table.join(movies_table,
                              movies_table.c.movieid == genres_table.c.movieid)
        )
        .join(countries_table, movies_table.c.movieid == countries_table.c.movieid)
        .where(
            and_(
                genres_table.c.genre.in_(genres),  # Filter genres
                countries_table.c.country == 'France',  # Only the French related Films
                genres_table.c.movieid != movie_id  # Exclude the current movie
            )
        )
        # Group by movie details
        .group_by(movies_table.c.movieid, movies_table.c.movietitle, movies_table.c.year)
        .order_by(movies_table.c.year.desc())  # Order by most recent movies
    )

    if most_related:
        having_clause = func.count(genres_table.c.genre) == len(
            genres)  # Exact genre match
    else:
        having_clause = and_(
            func.count(genres_table.c.genre) >= len(
                genres) / 2,  # Minimum threshold
            func.count(genres_table.c.genre) < len(
                genres)        # Exclude full matches
        )

    # Complete query
    query = base_query.having(having_clause)

    return [{"title": related_movie[0].split(" (")[0],
             "year": int(related_movie[1])}
            for related_movie in conn.execute(query).fetchall()[:10]]


def create_mongo_documents():
    """
    Creates all documents for France collection
    """

    with engine.connect() as connection:
        french_movies = get_french_movies(connection)

        for movie in french_movies:
            movie_id = movie[0]
            title = movie[1].split(" (")[0]
            year = int(movie[2])

            # Get all genres of the movie
            genres_query = (
                select(genres_table.c.genre)
                .where(genres_table.c.movieid == movie_id)
            )
            genres = [genre[0]
                      for genre in connection.execute(genres_query).fetchall()]

            # Get all directors of the movie
            directors_query = (
                select(
                    directors_table.c.directorname) .join(
                    directors_info_table,
                    directors_table.c.directorid == directors_info_table.c.directorid) .where(
                    directors_info_table.c.movieid == movie_id))
            directors = [director[0] for director in connection.execute(
                directors_query).fetchall()]

            # Get all actors of the movie
            actors_query = (
                select(
                    actors_table.c.actorname) .join(
                    actors_info_table,
                    actors_table.c.actorid == actors_info_table.c.actorid) .where(
                    actors_info_table.c.movieid == movie_id))
            actors = [actors[0]
                      for actors in connection.execute(actors_query).fetchall()]

            # Get most related movies based on genre coincidence
            most_related = get_related_movies(
                connection, movie_id, genres, most_related=True)

            # Get related movies based on genre coincidence
            related = get_related_movies(
                connection, movie_id, genres, most_related=False)

            # Create document for mongoDB database
            document = {
                "title": title,
                "genres": genres,
                "year": year,
                "directors": directors,
                "actors": actors,
                "most_related_movies": most_related,
                "related_movies": related,
            }

            mongo_collection.insert_one(document)


if __name__ == "__main__":
    create_mongo_documents()
    print("All data inserted in MongoDB successfully.")
