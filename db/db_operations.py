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
     data = {"user": username, "Basic achievements": [
        {"title": "First Flight", "description": "Achieve a score of 1 or more in one game", "target": 1, "progress": 0, "completed": False, "completion_date": None},
        {"title": "Novice Flyer", "description": "Achieve a score of 10 or more in one game", "target": 10, "progress": 0, "completed": False, "completion_date": None},
        {"title": "Intermediate Pilot", "description": "Achieve a score of 50 or more in one game", "target": 50, "progress": 0, "completed": False, "completion_date": None},
        {"title": "Expert Aviator", "description": "Achieve a score of 100 or more in one game", "target": 100, "progress": 0, "completed": False, "completion_date": None},
        {"title": "High Flyer", "description": "Achieve a score of 200 or more in one game", "target": 200, "progress": 0, "completed": False, "completion_date": None}],
        "Milestone achievements": [
        {"title": "Persistence Pays", "description": "Play 100 games", "target": 100, "progress": 0, "completed": False, "completion_date": None},
        {"title": "Dedicated Player", "description": "Play 500 games", "target": 500, "progress": 0, "completed": False, "completion_date": None},
        {"title": "True Fan", "description": "Play 1000 games", "target": 1000, "progress": 0, "completed": False, "completion_date": None},
        {"title": "Marathon Runner", "description": "Achieve a score of 10 000 points across all games", "target": 10000, "progress": 0, "completed": False, "completion_date": None}
    ]}
     achievements_col.insert_one(data)

def update_achievements(client: MongoClient, username: str, score: int):
     achievements_col = check_and_create_collection(client, "FlappyMuleAchievements")
     date_today = datetime.today().strftime('%Y-%m-%d')
     filter = {"user": username}
     test = achievements_col.find_one(filter)
     basic = test["Basic achievements"]
     milestone = test["Milestone achievements"]
     update = None
     for value in basic:
          progress = value.get("progress")
          completed = value.get("completed")
          title = value.get("title")
          target = value.get("target")
          filter2 = {"user": username, f"Basic achievements.title": title}
          if not completed and score > progress:
                if score >= target:
                    update = {"$set": {f'Basic achievements.$.progress': score, f'Basic achievements.$.completed': True, f'Basic achievements.$.completion_date': date_today}}
                else:
                    update = {"$set": {f'Basic achievements.$.progress': score}}
                achievements_col.update_one(filter2, update)
     for value in milestone:
          progress = value.get("progress")
          completed = value.get("completed")
          title = value.get("title")
          target = value.get("target")
          filter2 = {"user": username, f"Milestone achievements.title": title}
          val = 1
          if not completed:
                if title == "Marathon Runner":
                    val = score
                if score >= target:
                    update = {"$inc": {f'Milestone achievements.$.progress': val, f'Milestone achievements.$.completed': True, f'Basic achievements.$.completion_date': date_today}}
                else:
                    update = {"$inc": {f'Milestone achievements.$.progress': val}}
                achievements_col.update_one(filter2, update)


def check_and_create_collection(client: MongoClient, col_name):
        mydb = client["FlappyMule"]
        if col_name not in mydb.list_collection_names():
            mycol = mydb[col_name]
        mycol = mydb[col_name]
        return mycol
