from pymongo import MongoClient

from config import settings


MONGO_CLIENT = MongoClient(settings.MONGODB_URI)
GITCHAT_DB = MONGO_CLIENT['gitchat']