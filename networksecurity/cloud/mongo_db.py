import os
import sys

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging import logger

load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

try:

    client = MongoClient(
        MONGO_DB_URL,
        server_api=ServerApi("1")
    )

    client.admin.command("ping")

    logger.info("MongoDB Connected Successfully")

except Exception as e:

    raise NetworkSecurityException(e, sys)



if __name__ == "__main__":
    logger.info("Testing MongoDB Connection")