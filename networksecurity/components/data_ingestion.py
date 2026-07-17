from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

import os
import sys
import numpy as np
import pandas as pd
import pymongo
import certifi

from sklearn.model_selection import train_test_split

from dotenv import load_dotenv

load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")
ca = certifi.where()


class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_collection_as_dataframe(self) -> pd.DataFrame:
        """
        Read data from MongoDB collection and return a DataFrame.
        """
        try:
            logging.info("Reading data from MongoDB")

            if not MONGO_DB_URL:
                raise Exception(
                    "MONGO_DB_URL is not available in environment variables"
                )

            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name

            mongo_client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)

            try:
                collection = mongo_client[database_name][collection_name]

                records = list(collection.find())

                df = pd.DataFrame(records)

            finally:
                mongo_client.close()

            if df.empty:
                raise Exception(
                    f"No records found in collection '{collection_name}'"
                )

            if "_id" in df.columns:
                df.drop(columns=["_id"], inplace=True)

            df.replace({"na": np.nan}, inplace=True)

            logging.info(f"Dataframe shape: {df.shape}")

            return df

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_data_into_feature_store(
        self, dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        try:
            logging.info("Exporting data into feature store")

            feature_store_file_path = (
                self.data_ingestion_config.feature_store_file_path
            )

            dir_path = os.path.dirname(feature_store_file_path)

            os.makedirs(dir_path, exist_ok=True)

            dataframe.to_csv(
                feature_store_file_path,
                index=False,
                header=True,
            )

            logging.info(
                f"Feature store file saved at: {feature_store_file_path}"
            )

            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def split_data_as_train_test(self, dataframe: pd.DataFrame) -> None:
        try:
            logging.info("Performing train-test split")

            train_set, test_set = train_test_split(
                dataframe,
                test_size=self.data_ingestion_config.train_test_split_ratio,
                random_state=42,
            )

            logging.info(f"Train set shape: {train_set.shape}")
            logging.info(f"Test set shape: {test_set.shape}")

            dir_path = os.path.dirname(
                self.data_ingestion_config.training_file_path
            )

            os.makedirs(dir_path, exist_ok=True)

            train_set.to_csv(
                self.data_ingestion_config.training_file_path,
                index=False,
                header=True,
            )

            test_set.to_csv(
                self.data_ingestion_config.testing_file_path,
                index=False,
                header=True,
            )

            logging.info("Train and test datasets saved successfully")

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        try:
            logging.info("Starting Data Ingestion")

            dataframe = self.export_collection_as_dataframe()

            dataframe = self.export_data_into_feature_store(dataframe)

            self.split_data_as_train_test(dataframe)

            data_ingestion_artifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path,
            )

            logging.info("Data Ingestion completed successfully")

            return data_ingestion_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)
