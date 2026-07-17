import os
import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    ModelTrainerArtifact
)

import mlflow
import mlflow.sklearn
from urllib.parse import urlparse
import dagshub

from networksecurity.entity.config_entity import ModelTrainerConfig

from networksecurity.utils.ml_utils.model.estimator import NetworkModel

from networksecurity.utils.main_utils.utils import (
    save_object,
    load_object,
    load_numpy_array_data,
    evaluate_models
)

from networksecurity.utils.ml_utils.metric.classification_metric import (
    get_classification_score
)

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier
)

from xgboost import XGBClassifier



import mlflow
import mlflow.sklearn
from urllib.parse import urlparse





class ModelTrainer:
    def __init__(
        self,
        model_trainer_config: ModelTrainerConfig,
        data_transformation_artifact: DataTransformationArtifact
    ):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = (
                data_transformation_artifact
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)
        


    def track_mlflow(
            self,
            best_model,
            classificationmetric
        ):

        # Skip MLflow logging on Render to stay within the 512MB RAM limit
        if "RENDER" in os.environ:
            logging.info("Skipping MLflow logging on Render to conserve memory.")
            return

        with mlflow.start_run():

            f1_score = classificationmetric.f1_score
            precision_score = classificationmetric.precision_score
            recall_score = classificationmetric.recall_score

            mlflow.log_metric(
                "f1_score",
                f1_score
            )

            mlflow.log_metric(
                "precision_score",
                precision_score
            )

            mlflow.log_metric(
                "recall_score",
                recall_score
            )

            mlflow.sklearn.log_model(
                sk_model=best_model,
                name="model",
                serialization_format="pickle"
            )



    def train_model(
        self,
        X_train,
        y_train,
        X_test,
        y_test
    ):
        
        try:
            dagshub.init(
                repo_owner="mandy_07",
                repo_name="network_security",
                mlflow=True
            )
            logging.info("DagsHub initialized successfully.")
        except Exception as e:
            logging.warning(f"DagsHub initialization skipped: {e}")

        models = {
            "Random Forest": RandomForestClassifier(
                verbose=1,
                random_state=42
            ),

            "Decision Tree": DecisionTreeClassifier(random_state=42),

            "Gradient Boosting": GradientBoostingClassifier(
                verbose=1,
                random_state=42
            ),

            "Logistic Regression": LogisticRegression(
                verbose=1,
                max_iter=1000
            ),

            "AdaBoost": AdaBoostClassifier(random_state=42),

            "XGBoost": XGBClassifier(
                eval_metric="logloss",
                random_state=42
            )
        }

        params = {

            "Decision Tree": {
                "criterion": [
                    "gini",
                    "entropy",
                    "log_loss"
                ]
            },

            "Random Forest": {
                "n_estimators": [
                    8,
                    16,
                    32,
                    128,
                    256
                ]
            },

            "Gradient Boosting": {
                "learning_rate": [
                    0.1,
                    0.01,
                    0.05,
                    0.001
                ],
                "subsample": [
                    0.6,
                    0.7,
                    0.75,
                    0.85,
                    0.9
                ],
                "n_estimators": [
                    8,
                    16,
                    32,
                    64,
                    128,
                    256
                ]
            },

            "Logistic Regression": {},

            "AdaBoost": {
                "learning_rate": [
                    0.1,
                    0.01,
                    0.001
                ],
                "n_estimators": [
                    8,
                    16,
                    32,
                    64,
                    128,
                    256
                ]
            },

            "XGBoost": {
                "n_estimators": [
                    100,
                    200
                ],
                "max_depth": [
                    3,
                    5,
                    7
                ],
                "learning_rate": [
                    0.01,
                    0.1
                ]
            }
        }

        logging.info("Starting model evaluation")

        model_report = evaluate_models(
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            models=models,
            param=params
        )

        best_model_score = max(
            model_report.values()
        )

        best_model_name = list(
            model_report.keys()
        )[
            list(model_report.values()).index(
                best_model_score
            )
        ]

        best_model = models[best_model_name]

        logging.info(
            f"Best Model Found: {best_model_name}"
        )

        logging.info(
            f"Best Model Test F1 Score: {best_model_score}"
        )

        if (best_model_score < self.model_trainer_config.expected_accuracy):
            raise NetworkSecurityException(
                "No best model found with score greater than expected threshold",sys
            )

        # Fit best model explicitly
        best_model.fit(
            X_train,
            y_train
        )

        y_train_pred = best_model.predict(
            X_train
        )

        classification_train_metric = (
            get_classification_score(
                y_true=y_train,
                y_pred=y_train_pred
            )
        )

        ## Track the experiements with mlflow
        self.track_mlflow(best_model,classification_train_metric)




        y_test_pred = best_model.predict(
            X_test
        )

        classification_test_metric = (
            get_classification_score(
                y_true=y_test,
                y_pred=y_test_pred
            )
        )

        self.track_mlflow(best_model,classification_test_metric)


        preprocessor = load_object(
            self.data_transformation_artifact.transformed_object_file_path
        )

        network_model = NetworkModel(
            preprocessor=preprocessor,
            model=best_model
        )

        os.makedirs(
            os.path.dirname(
                self.model_trainer_config.trained_model_file_path
            ),
            exist_ok=True
        )

        save_object(
            file_path=self.model_trainer_config.trained_model_file_path,
            obj=network_model
        )

        logging.info(
            "Network model saved successfully"
        )


        save_object("final_model/model.pkl",best_model)

        model_trainer_artifact = (
            ModelTrainerArtifact(
                trained_model_file_path=
                self.model_trainer_config.trained_model_file_path,

                train_metric_artifact=
                classification_train_metric,

                test_metric_artifact=
                classification_test_metric
            )
        )

        logging.info(
            f"Model Trainer Artifact: "
            f"{model_trainer_artifact}"
        )

        return model_trainer_artifact

    def initiate_model_trainer(
        self
    ) -> ModelTrainerArtifact:

        try:

            train_arr = load_numpy_array_data(
                self.data_transformation_artifact.transformed_train_file_path
            )

            test_arr = load_numpy_array_data(
                self.data_transformation_artifact.transformed_test_file_path
            )

            X_train = train_arr[:, :-1]
            y_train = train_arr[:, -1]

            X_test = test_arr[:, :-1]
            y_test = test_arr[:, -1]

            model_trainer_artifact = (
                self.train_model(
                    X_train,
                    y_train,
                    X_test,
                    y_test
                )
            )

            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(
                e,
                sys
            ) 