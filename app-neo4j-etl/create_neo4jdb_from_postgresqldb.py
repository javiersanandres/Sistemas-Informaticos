from typing import List, Tuple, Any
import os
from dotenv import load_dotenv
import argparse
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from neo4j import GraphDatabase
from neo4j.exceptions import DriverError, Neo4jError

load_dotenv()

SQL_DATABASE_URI = os.getenv('SQL_DATABASE_URI')

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_PSWRD = os.getenv('NEO4J_PSWRD')
NEO4J_AUTH = ("neo4j", NEO4J_PSWRD)

def get_data_from_sql_database(url: str) -> Tuple[List[Any]]:
    """
    Gets the relevant data for the new Neo4j database. This includes the
    20 best-selling movies in the US and their respective actors and directors.
    """
    
    # Connect to SQL database
    engine = sql.create_engine(url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Fetch data from the database
    movies = get_best_selling_US_movies(session)

    # Get movie ids to reuse them to obtain the actors and directors
    movie_ids = [movie['movie_id'] for movie in movies]

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
                                        m.movieid AS movie_id,
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
                                        m.movieid
                                    ORDER BY
                                        SUM(i.sales) DESC
                                    LIMIT 20;
                                    """)
    movies_result = session.execute(best_selling_US_movies_query).mappings()
    movies = movies_result.all()
    
    return movies


def get_movie_actors(session: Any, movie_ids: List) -> List[Any]:
    """
    Gets the actors from the 20 best-selling movies from the US.
    """
    actors_query = sql.text("""
                            SELECT
                                m.movieid as movie_id,
                                a.actorid as actor_id,
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
    actors_result = session.execute(actors_query, {'movie_ids': tuple(movie_ids)}).mappings()
    actors = actors_result.all()
    
    return actors


def get_movie_directors(session: Any, movie_ids: List) -> List[Any]:
    """
    Gets the directors from the 20 best-selling movies from the US.
    """
    directors_query = sql.text("""
                            SELECT 
                                m.movieid as movie_id,
                                d.directorid AS director_id,
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
    directors_result = session.execute(directors_query, {'movie_ids': tuple(movie_ids)}).mappings()
    directors = directors_result.all()
    
    return directors


def build_neo4j_db(data: Tuple[Any], clear_data: bool = False) -> None:
    """
    Builds the new Neo4j database with the previously fetched data.
    """
    # Create controller
    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)

    # Fill the database with info
    try:
        with driver.session() as session:
            # Clear existing data, if requested
            if clear_data:
                print('[NEO4J-DB] Clearing existing data...')
                session.run('MATCH (n) DETACH DELETE n')
                print('[NEO4J-DB] Existing data cleared.')

            # Add new data
            add_movies(data[0], session)
            add_actors(data[1], session)
            add_directors(data[2], session)
    except (DriverError, Neo4jError) as exception:
        print(f'An error occurred: \n{exception}')
        driver.close()
        raise

    # Close controller after all
    driver.close()


def add_movies(movies_data: List[Any], session: Any) -> None:
    """
    Adds the info about the movies to the neo4j database.
    """
    for movie in movies_data:
        session.run("""
                    CREATE (m: Movie{movieId: $id, title: $title})
                    """,
                    id=int(movie['movie_id']), title=movie['title']
                )


def add_actors(actors_data: List[Any], session: Any) -> None:
    """
    Adds the info about the actors to the neo4j database.
    """
    for actor in actors_data:
        session.run("""
                    MATCH (m: Movie{movieId: $movie_id})
                    MERGE (a: Actor: Person {actorId: $actor_id, name: $name})
                    MERGE (a)-[:ACTED_IN]->(m)
                    """,
                    movie_id=int(actor['movie_id']), actor_id=int(actor['actor_id']),
                    name=actor['name']
                )


def add_directors(directors_data: List[Any], session: Any) -> None:
    """
    Adds the info about the directors to the neo4j database.
    """
    for director in directors_data:
        session.run("""
                    MATCH (m: Movie{movieId: $movie_id})
                    CREATE (d: Director: Person {directorId: $director_id, name: $name})
                    CREATE (d)-[:DIRECTED]->(m)
                    """,
                    movie_id=int(director['movie_id']), director_id=int(director['director_id']),
                    name=director['name']
                )


def parse_arguments():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Manage the Neo4j database")
    parser.add_argument("--clear_data", "-c", action="store_true",
        help="Clear existing data in the Neo4j database.")
    return parser.parse_args()


if __name__ == "__main__":
    # Check if "clear_data" option was selected
    args = parse_arguments()

    # Fetch data from SQL database
    print('[SQL-DB] Fetching data from SQL database...')
    movies, actors, directors = get_data_from_sql_database(SQL_DATABASE_URI)
    print('[SQL-DB] Data fetched correctly.')
    
    # Build the new Neo4j database
    print('[NEO4J-DB] Building neo4j database from the fetched data...')
    build_neo4j_db((movies, actors, directors), clear_data=args.clear_data)
    print('[NEO4J-DB] Database was built correctly. Visit \"localhost:7474\" to check the database.')