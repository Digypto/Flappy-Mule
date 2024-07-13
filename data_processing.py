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