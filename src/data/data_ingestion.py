import numpy as np
import pandas as pd
pd.set_option('future.no_silent_downcasting', True)
import os
import sys
from sklearn.model_selection import train_test_split
import yaml
import logging
from src.logger import logging
from src.exception import MyException
from src.connections.s3_connection import s3_operations

def load_params(params_path: str) -> dict:
    """Load parameters from a yaml file."""
    try:
        with open(params_path, 'r') as file:
            params = yaml.safe_load(file)
        logging.debug(f"Parameters retrieved from {params_path}")
        return params
    except Exception as e:
        raise MyException(e, sys) from e

def load_data(data_url: str) -> pd.DataFrame:
    """Load data from a CSV file."""
    try:
        df = pd.read_csv(data_url)
        logging.info(f"Data loaded from {data_url}")
        return df
    except Exception as e:
        raise MyException(e, sys) from e

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess the data."""
    try:
        logging.info("Pre-processsing started...")
        final_df = df[df['sentiment'].isin(['positive', 'negative'])]
        final_df['sentiment'] = final_df['sentiment'].replace({'positive': 1, 'negative': 0})
        logging.info("Data Preprocessing completed.")
        return final_df
    except Exception as e:
        raise MyException(e, sys) from e

def save_data(train_data: pd.DataFrame, test_data: pd.DataFrame, data_path: str) -> None:
    """Save the train and test data."""
    try:
        raw_data_path = os.path.join(data_path, 'raw')
        os.makedirs(raw_data_path, exist_ok=True)
        train_data.to_csv(os.path.join(raw_data_path, 'train.csv'), index=False)
        test_data.to_csv(os.path.join(raw_data_path, 'test.csv'), index=False)
        logging.info(f"Train and test data saved to {raw_data_path}.")
    except Exception as e:
        raise MyException(e, sys) from e

def main():
    try:
        params = load_params('params.yaml')
        test_size = params['data_ingestion']['test_size']
        # test_size = 0.2

        df = load_data(data_url="https://raw.githubusercontent.com/vikashishere/Datasets/refs/heads/main/data.csv")
        # s3 = s3_operations(bucket_name="review-analysis-project",
        #                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        #                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
        # df = s3.fetch_file_from_s3("data.csv")

        final_df = preprocess_data(df)
        train_data, test_data = train_test_split(final_df, test_size=test_size, random_state=42)
        save_data(train_data, test_data, data_path='./data')
    except Exception as e:
        raise MyException(e, sys) from e
    
if __name__ == "__main__":
    main()        