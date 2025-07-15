import json
import mlflow
import logging
from src.logger import logging
from src.exception import MyException
import sys
import os
import dagshub
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

def load_model_info(file_path: str) -> dict:
    """Load the model info from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            model_info = json.load(file)
        logging.info(f"Model info loaded from {file_path}")
        return model_info
    except Exception as e:
        raise MyException(e, sys) from e

def register_model(model_name: str, model_info: dict) -> None:
    """Registers the model to the MLFlow Registry..."""
    try:
        model_uri = f"runs:/{model_info['run_id']}/{model_info['model_path']}"
        
        # registers the model
        model_version = mlflow.register_model(model_uri, model_name)

        # Transition the model to "Staging" stage
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(
            name=model_name,
            version=model_version.version,
            stage="Staging"
        )
        logging.info(f"Model {model_name} version {model_version.version} registered and transitioned to Staging.")
    except Exception as e:
        raise MyException(e, sys) from e

def main():
    try:
        model_info_path = 'reports/experiment_info.json'
        model_info = load_model_info(model_info_path)

        model_name = "my_model"
        register_model(model_name, model_info)
    except Exception as e:
        raise MyException(e, sys) from e

if __name__ == "__main__":
    main()