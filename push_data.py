import os
import sys
import json

from dotenv import load_dotenv
load_dotenv()

import certifi
import pandas as pd
import pymongo

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logger


MONGO_DB_URL = os.getenv("MONGO_DB_URL")
ca = certifi.where()


class NetworkDataExtract:

    def __init__(self):

        try:
            self.client = pymongo.MongoClient(
                MONGO_DB_URL,
                tlsCAFile=ca,
                serverSelectionTimeoutMS=5000
            )

            # Verify connection
            self.client.admin.command("ping")
            logger.info("MongoDB Connected Successfully")
            self.db = self.client["network_security"]

        except Exception as e:
            raise NetworkSecurityException(e, sys)
        


    def csv_to_json(self, file_path):

        try:
            df = pd.read_csv(file_path)
            df.reset_index(drop=True, inplace=True)
            records = json.loads(
                df.to_json(orient="records")
            )
            logger.info("CSV file converted to JSON format")
            return records

        except Exception as e:
            raise NetworkSecurityException(e, sys)
        


    def insert_data_mongodb(self, collection_name, data):

        try:
            collection = self.db[collection_name]
            collection.insert_many(data)
            logger.info(
                f"{len(data)} records inserted into MongoDB successfully"
            )
            return len(data)

        except Exception as e:
            raise NetworkSecurityException(e, sys)




if __name__ == "__main__":

    FILE_PATH = r"Network_Data\phisingData.csv"

    COLLECTION_NAME = "NetworkData"

    network_obj = NetworkDataExtract()

    data = network_obj.csv_to_json(FILE_PATH)

    no_of_records = network_obj.insert_data_mongodb(
        COLLECTION_NAME,
        data
    )

    print(f"Number of records inserted: {no_of_records}")