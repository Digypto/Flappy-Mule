from db.db_connection import get_db_connection, retrieve_db_credentials
from pymongo import MongoClient


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
        # Retrieve top 10 scores
        data = {"user": "test_mule", "score": score}
        highscores_col.insert_one(data)
    except Exception as e:
        print(f"Error saving score: {e}")

def get_high_scores(client: MongoClient, limit: int = 10) -> list:
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
        return highscores_col
    except Exception as e:
        print(f"Error retrieving high scores: {e}")

def check_and_create_collection(client: MongoClient):
        mydb = client["FlappyMule"]
        if "FlappyMuleScores" not in mydb.list_collection_names():
            mycol = mydb["FlappyMuleScores"]
        mycol = mydb["FlappyMuleScores"]
        return mycol
