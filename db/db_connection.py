import os
from pymongo import MongoClient


def get_db_connection(user: str, password: str, host: str, appname: str) -> MongoClient:
    """
    Establishes a connection to the MongoDB database.

    Parameters
    ----------
    dbname : str
        Name of the MongoDB database.
    user : str
        Username for authentication (if required by MongoDB configuration).
    password : str
        Password for authentication (if required by MongoDB configuration).
    host : str
        Hostname or IP address of the MongoDB server (MongoDB Atlas cluster URI).
    appname : str
        The name of the app

    Returns
    -------
    pymongo.MongoClient
        The MongoDB client object.
    """
    try:
        conn_str = f"mongodb+srv://{user}:{password}@{host}/?retryWrites=true&w=majority&appName={appname}"
        client = MongoClient(conn_str)
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

def retrieve_db_credentials():
    credential_dict = {}
    with open(f"{os.getcwd()}/db/db_credentials.txt", "r") as f:
        for line in f:
            line = line.strip("\n")
            line = line.split("=")
            line_str = line[0].strip()
            line_id = line[1].strip()
            credential_dict[line_str] = line_id

    return credential_dict