import sys
import pandas as pd

from networksecurity.constants.training_pipeline import SCHEMA_FILE_PATH
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.utils.main_utils.utils import read_yaml_file


def validate_uploaded_file(file):
    """
    Validate uploaded file before reading it.
    """

    try:

        if file is None:
            raise ValueError("No file uploaded.")

        if file.filename == "":
            raise ValueError("File name cannot be empty.")

        if not file.filename.lower().endswith(".csv"):
            raise ValueError(
                "Only CSV files are allowed."
            )

        return True

    except Exception as e:
        raise NetworkSecurityException(e, sys)


def validate_prediction_dataframe(df: pd.DataFrame):
    """
    Validate dataframe before prediction.
    """

    try:

        if df.empty:
            raise ValueError(
                "Uploaded CSV is empty."
            )

        schema = read_yaml_file(SCHEMA_FILE_PATH)

        expected_columns = [
            list(col.keys())[0]
            for col in schema["columns"]
            if list(col.keys())[0] != "Result"
        ]

        uploaded_columns = list(df.columns)

        missing_columns = list(
            set(expected_columns) - set(uploaded_columns)
        )

        extra_columns = list(
            set(uploaded_columns) - set(expected_columns)
        )

        if missing_columns:
            raise ValueError(
                f"Missing columns: {missing_columns}"
            )

        if extra_columns:
            raise ValueError(
                f"Unexpected columns: {extra_columns}"
            )

        return True

    except Exception as e:
        raise NetworkSecurityException(e, sys)