import numpy as np
import pandas as pd
import os
import sys
from sklearn.feature_extraction.text import CountVectorizer
import yaml
from src.logger import logging
from src.exception import MyException
import pickle

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

def apply_bow(train_data: pd.DataFrame, test_data: pd.DataFrame, max_feature: int) -> tuple:
    """Apply count vectorizer to the data."""
    try:
        logging.info("Applying BOW...")
        vectorizer = CountVectorizer(max_features=max_feature)

        X_train = train_data['review'].values
        y_train = train_data['sentiment'].values
        X_test = test_data['review'].values
        y_test = test_data['sentiment'].values

        X_train_bow = vectorizer.fit_transform(X_train)
        X_test_bow = vectorizer.transform(X_test)

        train_df = pd.DataFrame(X_train_bow.toarray())
        train_df['label'] = y_train

        test_df = pd.DataFrame(X_test_bow.toarray())
        test_df['label'] = y_test

        pickle.dump(vectorizer, open('models/vectorizer.pkl', 'wb'))
        logging.info("Bag of words applied and data transformed.")

        return train_df, test_df
    except Exception as e:
        raise MyException(e, sys) from e
    
def save_data(df: pd.DataFrame, file_path: str) -> None:
    """Save the dataframe to a CSV file."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_csv(file_path, index=False)
        logging.info(f"Data saved to {file_path}.")
    except Exception as e:
        raise MyException(e, sys) from e
    
def main():
    try:
        params = load_params('params.yaml')
        max_features = params['feature_engineering']['max_features']
        # max_features = 20

        train_data = load_data("./data/interim/train_processed.csv")
        test_data = load_data("./data/interim/test_processed.csv")

        train_df, test_df = apply_bow(train_data, test_data, max_features)

        save_data(train_df, os.path.join("./data", "processed", "train_bow.csv"))
        save_data(test_df, os.path.join("./data", "processed", "test_bow.csv"))

        logging.info("Feature engineering done.")
    except Exception as e:
        raise MyException(e, sys) from e

if __name__ == "__main__":
    main()