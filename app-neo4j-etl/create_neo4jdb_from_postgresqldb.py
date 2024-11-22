from typing import List, Tuple, Any
import os
from dotenv import load_dotenv
import sqlalchemy as sql
from neo4j import GraphDatabase, RoutingControl

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def get_data_from_sql_database(url: str) -> Tuple[List[Any]]:
    """
    Gets the relevant data for the new Neo4j database. This includes the
    20 best-selling movies in the US and their respective actors and directors.
    """
    
    # Connect to SQL database
    engine = sql.create_engine(DATABASE_URL)
    Session = sql.orm.sessionmaker(bind=engine)
    session = Session()
    
    # Fetch data from the database
    movies = get_best_selling_US_movies(session)

    # Get movie ids to reuse them to obtain the actors and directors
    movie_ids = [movie['id'] for movie in movies]

    actors = get_movie_actors(session, movie_ids)
    directors = get_movie_directors(session, movie_ids)

    # Close the session
    session.close()

    return movies, actors, directors


def get_best_selling_US_movies(session: Any) -> List[Any]:
    """
    Gets the 20 best-selling movies from the US.
    """
    best_selling_US_movies_query = sql.text("""
                                    SELECT
                                        m.movieid as movieId,
                                        m.movietitle AS title
                                    FROM
                                        imdb_movies m
                                    JOIN
                                        products p ON m.movieid = p.movieid
                                    JOIN
                                        inventory i ON p.prod_id = i.prod_id
                                    JOIN
                                        imdb_moviecountries mc ON m.movieid = mc.movieid
                                    WHERE
                                        mc.country = 'USA'
                                    GROUP BY
                                        m.movieid, m.movietitle, m.year
                                    ORDER BY
                                        SUM(i.sales) DESC
                                    LIMIT 20;
                                    """)
    movies_result = session.execute(best_selling_US_movies_query)
    movies = movies_result.fetchall()
    
    return movies


def get_movie_actors(session: Any, movie_ids: List) -> List[Any]:
    """
    Gets the actors from the 20 best-selling movies from the US.
    """
    actors_query = sql.text("""
                            SELECT
                                m.movieid,
                                a.actorid as actorId,
                                a.actorname AS name
                            FROM
                                imdb_movies m
                            JOIN
                                imdb_actormovies am ON m.movieid = am.movieid
                            JOIN
                                imdb_actors a ON am.actorid = a.actorid
                            WHERE
                                m.movieid IN :movie_ids;
                            """)
    actors_result = session.execute(actors_query, {'movie_ids': tuple(movie_ids)})
    actors = actors_result.fetchall()
    
    return actors


def get_movie_directors(session: Any, movie_ids: List) -> List[Any]:
    """
    Gets the directors from the 20 best-selling movies from the US.
    """
    directors_query = sql.text("""
                            SELECT 
                                m.movieid,
                                m.movietitle AS movie_title,
                                d.directorid AS directorId,
                                d.directorname AS name
                            FROM 
                                imdb_movies m
                            JOIN 
                                imdb_directormovies dm ON m.movieid = dm.movieid
                            JOIN 
                                imdb_directors d ON dm.directorid = d.directorid
                            WHERE 
                                m.movieid IN :movie_ids
                            """)
    directors_result = session.execute(directors_query, {'movie_ids': tuple(movie_ids)})
    directors = directors_result.fetchall()
    
    return directors


if __name__ == "__main__":
    movies, actors, directors = get_data_from_sql_database(DATABASE_URL)

    # Mostrar las 20 películas más vendidas
    print("Top 20 Best-Selling Movies:")
    for movie in movies:
        print(f"Movie ID: {movie['movieid']}, Title: {movie['movie_title']}, Year: {movie['year']}, Total Sales: {movie['total_sales']}")

    # Mostrar los actores de las 20 películas más vendidas
    print("\nActors in the Top 20 Best-Selling Movies:")
    for actor in actors:
        print(f"Movie Title: {actor['movie_title']}, Actor: {actor['actor_name']}")

    # Mostrar los directores de las 20 películas más vendidas
    print("\nDirectors of the Top 20 Best-Selling Movies:")
    for director in directors:
        print(f"Movie Title: {director['movie_title']}, Director: {director['director_name']}")
