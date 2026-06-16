from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig
)
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

import sys


if __name__ == "__main__":
    try:
        logging.info("Starting Training Pipeline")

        # Training Pipeline Config
        training_pipeline_config = TrainingPipelineConfig()

        # Data Ingestion Config
        data_ingestion_config = DataIngestionConfig(
            training_pipeline_config=training_pipeline_config
        )

        # Data Ingestion Component
        data_ingestion = DataIngestion(
            data_ingestion_config=data_ingestion_config
        )

        # Run Data Ingestion
        data_ingestion_artifact = (
            data_ingestion.initiate_data_ingestion()
        )

        logging.info(
            f"Data Ingestion Artifact: {data_ingestion_artifact}"
        )

        print("\nData Ingestion Completed Successfully")
        print(data_ingestion_artifact)

    except Exception as e:
        raise NetworkSecurityException(e, sys)


