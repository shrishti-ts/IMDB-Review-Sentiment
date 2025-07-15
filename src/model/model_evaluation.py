import numpy as np
import pandas as pd
import pickle
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, f1_score
from sklearn.linear_model import LogisticRegression
import logging
import mlflow
import mlflow.sklearn
import dagshub
import os
import sys
from src.logger import logging
from src.exception import MyException
import warnings

warnings.simplefilter("ignore", UserWarning)
warnings.filterwarnings("ignore")
logging.getLogger("urllib3").setLevel(logging.ERROR)

# Below is the code for production use
# -------------------------------------------------------------------------------------
# Set up DagsHub credentials for MLflow tracking
dagshub_token = os.getenv("CAPSTONE_TEST")
if not dagshub_token:
    raise EnvironmentError("CAPSTONE_TEST environment variable is not set")

os.environ["MLFLOW_TRACKING_USERNAME"] = dagshub_token
os.environ["MLFLOW_TRACKING_PASSWORD"] = dagshub_token

dagshub_url = "https://dagshub.com"
repo_owner = "keshav1017"
repo_name = "Capstone-Project"

# Set up MLflow tracking URI
mlflow.set_tracking_uri(f'{dagshub_url}/{repo_owner}/{repo_name}.mlflow')

# Below is the code for local use

# mlflow.set_tracking_uri('https://dagshub.com/keshav1017/Capstone-Project.mlflow')
# dagshub.init(repo_owner='keshav1017', repo_name='Capstone-Project', mlflow=True)

def load_model(file_path: str) -> LogisticRegression:
    try:
        with open(file_path, 'rb') as file:
            model = pickle.load(file)
        logging.info(f"Model loaded from {file_path}")
        return model
    except Exception as e:
        raise MyException(e, sys) from e
    
def load_data(file_path: str) -> pd.DataFrame:
    """Load data from a CSV file."""
    try:
        df = pd.read_csv(file_path)
        logging.info(f"Data loaded from {file_path}")
        return df
    except Exception as e:
        raise MyException(e, sys) from e

def evaluate_model(clf: LogisticRegression, X_test: np.ndarray, y_test: np.ndarray) -> dict:
    try:
        y_pred = clf.predict(X_test)
        y_pred_proba = clf.predict_proba(X_test)[:,-1]

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_pred_proba)

        metrics_dict = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'auc': auc
        }
        logging.info('Model evaluation metrics calculated')
        return metrics_dict
    except Exception as e:
        raise MyException(e, sys) from e

def save_metrics(metrics: dict, file_path: str) -> None:
    try:
        with open(file_path, 'w') as file:
            json.dump(metrics, file, indent=4)
        logging.info(f"Metrics save to {file_path}")
    except Exception as e:
        raise MyException(e, sys) from e

def save_model_info(run_id: str, model_path: str, file_path: str) -> None:
    """Save the model run ID and path to a json file."""
    try:
        model_info = {'run_id': run_id, 'model_path': model_path}
        with open(file_path, 'w') as file:
            json.dump(model_info, file, indent=4)
        logging.info(f"Model info saved to {file_path}")
    except Exception as e:
        raise MyException(e, sys) from e

def main():
    mlflow.set_experiment("dvc-pipeline")
    with mlflow.start_run() as run:
        try:
            clf = load_model('./models/model.pkl')
            test_data = load_data('./data/processed/test_bow.csv')

            X_test = test_data.iloc[:, :-1].values
            y_test = test_data.iloc[:, -1].values

            metrics = evaluate_model(clf, X_test, y_test)

            save_metrics(metrics, 'reports/metrics.json')

            # log metrics to MLFlow
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)
            
            # log the model parameters to MLFlow
            if hasattr(clf, 'get_params'):
                params = clf.get_params()
                for param_name, param_value in params.items():
                    mlflow.log_param(param_name, param_value)
            
            # log model to MLFlow 
            mlflow.sklearn.log_model(clf, "model")

            # Save the model info
            save_model_info(run.info.run_id, "model", 'reports/experiment_info.json')

            # log the metrics file to MLFlow
            mlflow.log_artifact('reports/metrics.json')
        except Exception as e:
            raise MyException(e, sys) from e

if __name__ == "__main__":
    main()