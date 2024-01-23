import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import platform
import os


def client():
    if platform.system() == 'Linux':
        mongoUser = os.environ['mongoUser']
        mongoPass = os.environ['mongoPassword']
    else:
        with open("passwords.json", "rb") as f:
            passwords = json.load(f)
            mongoUser = passwords['mongoUser']
            mongoPass = passwords['mongoPassword']

    uri = "mongodb+srv://" + mongoUser + ":" + mongoPass + "@cluster0.udbes1y.mongodb.net/?retryWrites=true&w=majority"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    return client