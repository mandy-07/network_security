import os
import sys

import certifi
import pandas as pd
import pymongo

from dotenv import load_dotenv

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from uvicorn import run as app_run

from networksecurity.utils.validation import (
    validate_uploaded_file,
    validate_prediction_dataframe
)

from networksecurity.constants.training_pipeline import (
    DATA_INGESTION_COLLECTION_NAME,
    DATA_INGESTION_DATABASE_NAME,
)

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel


# ====================================================
# Load Environment Variables
# ====================================================

load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

if MONGO_DB_URL is None:
    raise Exception("MONGO_DB_URL environment variable not found.")

ca = certifi.where()


# ====================================================
# MongoDB Connection
# ====================================================

client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)

database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

logging.info("MongoDB connection established successfully.")


# ====================================================
# FastAPI App
# ====================================================

app = FastAPI(
    title="Network Intrusion Detection System API",
    description="REST API for detecting malicious network traffic using Machine Learning",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="./templates")


# ====================================================
# Load Model Once
# ====================================================

logging.info("Loading preprocessor and model...")

preprocessor = load_object("final_model/preprocessor.pkl")
final_model = load_object("final_model/model.pkl")

network_model = NetworkModel(
    preprocessor=preprocessor,
    model=final_model
)

logging.info("Model loaded successfully.")


# ====================================================
# Home Route
# ====================================================

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")


# ====================================================
# Train Route
# ====================================================

@app.get("/train")
async def train_route():
    try:

        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()

        return Response("Training completed successfully.")

    except Exception as e:
        raise NetworkSecurityException(e, sys)


# ====================================================
# Prediction Route
# ====================================================

@app.post("/predict")
async def predict_route(
    request: Request,
    file: UploadFile = File(...)
):
    try:

        # -----------------------------
        # Validate Uploaded File
        # -----------------------------

        validate_uploaded_file(file)

        # -----------------------------
        # Read CSV
        # -----------------------------

        df = pd.read_csv(file.file)

        # -----------------------------
        # Validate DataFrame
        # -----------------------------

        validate_prediction_dataframe(df)

        # -----------------------------
        # Predict
        # -----------------------------

        predictions = network_model.predict(df)

        df["Prediction"] = predictions

        # -----------------------------
        # Summary Statistics
        # -----------------------------

        total_records = len(df)

        legitimate_records = (df["Prediction"] == 1).sum()

        phishing_records = (df["Prediction"] == 0).sum()

        # -----------------------------
        # Convert Labels
        # -----------------------------

        df["Threat Status"] = df["Prediction"].map(
            {
                1: "🟢 Legitimate",
                0: "🔴 Phishing"
            }
        )

        df.drop(columns=["Prediction"], inplace=True)

        # -----------------------------
        # Save Prediction CSV
        # -----------------------------

        os.makedirs("prediction_output", exist_ok=True)

        output_path = os.path.join(
            "prediction_output",
            "output.csv"
        )

        df.to_csv(output_path, index=False)

        # -----------------------------
        # Convert Table to HTML
        # -----------------------------

        table_html = df.to_html(
            classes="table table-striped",
            index=False,
            escape=False
        )

        # -----------------------------
        # Return Dashboard
        # -----------------------------

        return templates.TemplateResponse(
            request=request,
            name="table.html",
            context={
                "table": table_html,
                "total_records": total_records,
                "legitimate_records": legitimate_records,
                "phishing_records": phishing_records
            }
        )

    except Exception as e:
        raise NetworkSecurityException(e, sys)


# ====================================================
# Run FastAPI
# ====================================================

if __name__ == "__main__":
    app_run(
        app,
        host="0.0.0.0",
        port=8000
    )