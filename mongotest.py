import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
import json
from flask import Flask

app = Flask(__name__)


with open("passwords.json", "rb") as f:
    passwords = json.load(f)
    mongoUser = passwords['mongoUser']
    mongoPass = passwords['mongoPassword']
uri = "mongodb+srv://"+mongoUser+":"+mongoPass+"@cluster0.udbes1y.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
