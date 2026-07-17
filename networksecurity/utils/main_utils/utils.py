import yaml
import os
import sys
import numpy as np
import pickle

from sklearn.metrics import f1_score
from sklearn.model_selection import GridSearchCV

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging


def read_yaml_file(file_path: str) -> dict:
    try:
        with open(file_path, "rb") as yaml_file:
            return yaml.safe_load(yaml_file)

    except Exception as e:
        raise NetworkSecurityException(e, sys)


def write_yaml_file(
    file_path: str,
    content: object,
    replace: bool = False
) -> None:
    try:

        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)

        os.makedirs(
            os.path.dirname(file_path),
            exist_ok=True
        )

        with open(file_path, "w") as file:
            yaml.dump(content, file)

    except Exception as e:
        raise NetworkSecurityException(e, sys)


def save_numpy_array_data(
    file_path: str,
    array: np.ndarray
):
    """
    Save numpy array data to file.
    """

    try:

        dir_path = os.path.dirname(file_path)

        os.makedirs(
            dir_path,
            exist_ok=True
        )

        with open(file_path, "wb") as file_obj:
            np.save(file_obj, array)

    except Exception as e:
        raise NetworkSecurityException(e, sys) from e


def save_object(
    file_path: str,
    obj: object
) -> None:

    try:

        logging.info(
            "Entered the save_object method of MainUtils class"
        )

        os.makedirs(
            os.path.dirname(file_path),
            exist_ok=True
        )

        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)

        logging.info(
            "Exited the save_object method of MainUtils class"
        )

    except Exception as e:
        raise NetworkSecurityException(e, sys) from e


def load_object(file_path: str) -> object:

    try:

        if not os.path.exists(file_path):
            raise Exception(
                f"The file: {file_path} does not exist"
            )

        with open(file_path, "rb") as file_obj:
            return pickle.load(file_obj)

    except Exception as e:
        raise NetworkSecurityException(e, sys) from e


def load_numpy_array_data(
    file_path: str
) -> np.ndarray:
    """
    Load numpy array data from file.

    Args:
        file_path (str): Location of file to load

    Returns:
        np.ndarray: Loaded numpy array
    """

    try:

        with open(file_path, "rb") as file_obj:
            return np.load(file_obj)

    except Exception as e:
        raise NetworkSecurityException(e, sys) from e


def evaluate_models(
    X_train,
    y_train,
    X_test,
    y_test,
    models,
    param
):
    """
    Evaluate classification models using GridSearchCV
    and return model performance report.
    """

    try:

        report = {}

        for model_name, model in models.items():

            logging.info(
                f"Training model: {model_name}"
            )

            para = param[model_name]

            # Detect Render free tier to prevent Out Of Memory crashes by using 1 worker
            default_n_jobs = 1 if "RENDER" in os.environ else -1
            n_jobs = int(os.getenv("GRIDSEARCH_N_JOBS", default_n_jobs))

            gs = GridSearchCV(
                estimator=model,
                param_grid=para,
                cv=3,
                n_jobs=n_jobs
            )

            gs.fit(X_train, y_train)

            model.set_params(
                **gs.best_params_
            )

            model.fit(
                X_train,
                y_train
            )

            y_train_pred = model.predict(
                X_train
            )

            y_test_pred = model.predict(
                X_test
            )

            train_model_score = f1_score(
                y_train,
                y_train_pred
            )

            test_model_score = f1_score(
                y_test,
                y_test_pred
            )

            logging.info(
                f"{model_name} Train F1 Score: "
                f"{train_model_score}"
            )

            logging.info(
                f"{model_name} Test F1 Score: "
                f"{test_model_score}"
            )

            report[model_name] = test_model_score

        return report

    except Exception as e:
        raise NetworkSecurityException(e, sys) from e