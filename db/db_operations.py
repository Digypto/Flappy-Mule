from db.db_connection import retrieve_db_credentials
from pymongo import MongoClient
import pymongo


credential_dict = retrieve_db_credentials()
dbname = credential_dict.get("dbname")
user = credential_dict.get("user")
password = credential_dict.get("password")
host = credential_dict.get("host")
port = credential_dict.get("port")

def save_score(client: MongoClient, score: int) -> None:
    """
    Saves the score to the 'highscores' collection in MongoDB.

    Parameters
    ----------
    client : pymongo.MongoClient
        MongoDB client object.
    score : int
        The score to be saved.
    """
    try:
        highscores_col = check_and_create_collection(client)
        num_documents = highscores_col.count_documents({})
        lowest_score_doc = highscores_col.find().sort('score', pymongo.ASCENDING).limit(1)
        if num_documents < 5:
            data = {"user": "test_mule", "score": score}
            highscores_col.insert_one(data)
        if score > lowest_score_doc[0]['score'] and num_documents >= 5:
            data = {"user": "test_mule", "score": score}
            highscores_col.insert_one(data)
            highscores_col.delete_one({"_id": lowest_score_doc[0]['_id']}) #Deleting the worst entry
    except Exception as e:
        print(f"Error saving score: {e}")

def get_high_scores(client: MongoClient) -> list:
    """
    Retrieves the top high scores from the 'highscores' collection in MongoDB.

    Parameters
    ----------
    client : pymongo.MongoClient
        MongoDB client object.
    limit : int, optional
        The number of high scores to retrieve (default is 10).

    Returns
    -------
    list of dict
        A list containing scores.
    """
    try:
        db = client["FlappyMule"]
        highscores_col = db['FlappyMuleScores']
        sorted_scores = highscores_col.find().sort('score', pymongo.DESCENDING).limit(5)
        return sorted_scores
    except Exception as e:
        print(f"Error retrieving high scores: {e}")

def get_worst_score_in_db(client: MongoClient):
        db = client["FlappyMule"]
        highscores_col = db['FlappyMuleScores']
        sorted_scores = highscores_col.find().sort('score', pymongo.DESCENDING).limit(5)
        worst_val = 0
        num_of_docs = 0
        for score_doc in sorted_scores:
            score_value = score_doc.get('score')
            worst_val = score_value
            num_of_docs += 1
        return worst_val, num_of_docs

def check_and_create_collection(client: MongoClient):
        mydb = client["FlappyMule"]
        if "FlappyMuleScores" not in mydb.list_collection_names():
            mycol = mydb["FlappyMuleScores"]
        mycol = mydb["FlappyMuleScores"]
        return mycol
