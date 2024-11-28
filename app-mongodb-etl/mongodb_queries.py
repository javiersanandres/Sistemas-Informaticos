from pymongo import MongoClient

def first_query(db):
    print("SHOWING ALL FRENCH SCIENCE FICTION MOVIES BETWEEN 1994 AND 1998")
    query = {"year": {"$gte": 1994, "$lte": 1998}, "genres": {"$in": ["Sci-Fi"]}}
    results = db.find(query, {"_id": 0})
    for result in results:
        print(result)
    print()

def second_query(db):
    print("SHOWING ALL FRENCH 1998 DRAMAS WITH TITLE STARTING WITH \'THE\'")
    query = {"year": { "$eq": 1998 }, "title" : { "$regex": ", The"}, "genres": { "$in": ["Drama"] }}
    results = db.find(query, {"_id": 0})
    for result in results:
        print(result)
    print()

def third_query(db):
    print("SHOWING ALL FRENCH FILMS IN WHICH AYE DUNAWAY y VIGGO MORTENSEN HAVE BOTH PLAYED")
    query = { "actors": { "$all": ["Dunaway, Faye", "Mortensen, Viggo"] } }
    results = db.find(query, {"_id": 0})
    for result in results:
        print(result)
    print()



if __name__ == "__main__":
    MONGODB_URL = "mongodb://localhost:27017/"
    MONGO_DB_NAME = "si1"
    MONGO_COLLECTION_NAME = "france"

    client = MongoClient(MONGODB_URL)
    mongo_db = client[MONGO_DB_NAME]
    mongo_collection = mongo_db[MONGO_COLLECTION_NAME]
    first_query(mongo_collection)
    second_query(mongo_collection)
    third_query(mongo_collection)

