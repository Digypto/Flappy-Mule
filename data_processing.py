import pandas as pd


from db.db_connection import get_db_connection


def database_to_dataframe(collection: str) -> pd.DataFrame:
    client = get_db_connection()
    db = client["FlappyMule"]
    df = None
    if collection == 'users':
        col = db['FlappyMuleUsers'].find()
        df = pd.DataFrame(list(col))
    if collection == 'scores':
        col = db['FlappyMuleScores'].find()
        df = pd.DataFrame(list(col))
    if collection == 'achievements':
        col = db['FlappyMuleAchievements'].find()
        df = pd.DataFrame(list(col))


    return df

def achievement_progress_to_dict(player, header: str) -> dict:
    try:
        df = database_to_dataframe("achievements")
        df = df.loc[df["user"] == player.get_name()]
        if df.empty:
            return {"text": [{"title": "Sign in to see achievements"}]}
        df_dict = df.to_dict()
        achievements_dict = {}
        if header == "Basic achievements":
            achievements_dict["Basic achievements"] = df_dict.get("Basic achievements")[0]
        if header == "Milestone achievements":
            achievements_dict["Milestone achievements"] = df_dict.get("Milestone achievements")[0]
        return achievements_dict
    except Exception as e:
        pass
