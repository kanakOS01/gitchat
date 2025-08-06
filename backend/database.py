from contextlib import asynccontextmanager
from pydoc import cli

from pymongo import MongoClient

from config import settings


async def mongo_db():
    client = MongoClient(settings.MONGODB_URI)
    db = client[settings.DB_NAME]
    try:
        yield db
    finally:
        client.close()