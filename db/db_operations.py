from pymongo import MongoClient
import pymongo
from datetime import datetime


def save_score(client: MongoClient, score: int, name: str) -> None:
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
        highscores_col = check_and_create_collection(client, "FlappyMuleScores")
        num_documents = highscores_col.count_documents({})
        lowest_score_doc = highscores_col.find().sort('score', pymongo.ASCENDING).limit(1)
        if num_documents < 5 and name != "":
            data = {"user": name, "score": score}
            highscores_col.insert_one(data)
        if score > lowest_score_doc[0]['score'] and num_documents >= 5 and name != "":
            data = {"user": name, "score": score}
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
        The number of high scores to retrieve (default is 5).

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

def save_user(client: MongoClient, username: str, password: str):
        date_today = datetime.today().strftime('%Y-%m-%d')
        try:
            users_col = check_and_create_collection(client, "FlappyMuleUsers")
            data = {"user": username, "password": password, "score": 0, "last_sign_in": date_today}
            users_col.insert_one(data)
        except Exception as e:
            print(f"Error saving user: {e}")

def update_user_lifetime_score(client: MongoClient, username: str, score: int):
        try:
            achievements_col = check_and_create_collection(client, "FlappyMuleAchievements")
            #data = {{"user": username}, {"$set":{"score": score}}}
            achievements_col.find_one_and_update({"user": username}, {"$inc":{"marathon_runner_progress": score}})
            #users_col.update_many({"score": {"$exists": False}}, {"$set": {"score": score}})
        except Exception as e:
            print(f"Error saving score: {e}")

def update_user_latest_sign_in(client: MongoClient, username: str):
        date_today = datetime.today().strftime('%Y-%m-%d')
        try:
            users_col = check_and_create_collection(client, "FlappyMuleUsers")
            users_col.find_one_and_update({"user": username}, {"$set":{"last_sign_in": date_today}})
            #users_col.update_many({"last_sign_in": {"$exists": False}}, {"$set": {"last_sign_in": date_today}})
        except Exception as e:
            print(f"Error saving date: {e}")

def get_users(client: MongoClient):
        try:
            db = client["FlappyMule"]
            users_col = db['FlappyMuleUsers'].find()
            return users_col
        except Exception as e:
            print(f"Error retrieving users: {e}")

def insert_achievements(client: MongoClient, username: str):
     achievements_col = check_and_create_collection(client, "FlappyMuleAchievements")
     data = {"user": username, "first_flight_completed": False, "first_flight_completion_date": None,
            "novice_flyer_completed": False, "novice_flyer_progress": 0, "novice_flyer_completion_date": None,
            "intermediate_pilot_completed": False, "intermediate_pilot_progress": 0, "intermediate_pilot_completion_date": None,
            "expert_aviator_completed": False, "expert_aviator_progress": 0, "expert_aviator_completion_date": None,
            "high_flyer_completed": False, "high_flyer_progress": 0, "high_flyer_completion_date": None,
            "persistence_pays_completed": False, "persistence_pays_progress": 0, "persistence_pays_completion_date": None,
            "dedicated_player_completed": False, "dedicated_player_progress": 0, "dedicated_player_completion_date": None,
            "true_fan_completetd": False, "true_fan_progress": 0, "true_fan_completion_date": None,
            "marathon_runner_completed": False, "marathon_runner_progress": 0, "marathon_runner_completion_date": None
            }
     achievements_col.insert_one(data)

def update_achievements(client: MongoClient, username: str):
     achievements_col = check_and_create_collection(client, "FlappyMuleAchievements")
     data = {"user": username, "first_flight_completed": False, "first_flight_completion_date": None,
            "novice_flyer_completed": False, "novice_flyer_progress": 0, "novice_flyer_completion_date": None,
            "intermediate_pilot_completed": False, "intermediate_pilot_progress": 0, "intermediate_pilot_completion_date": None,
            "expert_aviator_completed": False, "expert_aviator_progress": 0, "expert_aviator_completion_date": None,
            "high_flyer_completed": False, "high_flyer_progress": 0, "high_flyer_completion_date": None,
            "persistence_pays_completed": False, "persistence_pays_progress": 0, "persistence_pays_completion_date": None,
            "dedicated_player_completed": False, "dedicated_player_progress": 0, "dedicated_player_completion_date": None,
            "true_fan_completetd": False, "true_fan_progress": 0, "true_fan_completion_date": None,
            "marathon_runner_completed": False, "marathon_runner_progress": 0, "marathon_runner_completion_date": None
            }
     achievements_col.insert_one(data)

def check_and_create_collection(client: MongoClient, col_name):
        mydb = client["FlappyMule"]
        if col_name not in mydb.list_collection_names():
            mycol = mydb[col_name]
        mycol = mydb[col_name]
        return mycol
