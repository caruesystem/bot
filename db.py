from pymongo import MongoClient
from decouple import config


string = config("new_db_str")

def conn_sync():
    while True:
        try:
            client_sync = MongoClient()
        except:
            continue
        else:
            return client_sync.bot


sync_bot = MongoClient(string)
db = sync_bot["bot2"]
bot_cache = db["cache"]
bot_doc = db["doc"]
bot_image = db["image"]
bot_state = db["state"]
bot_game = db["game"]








