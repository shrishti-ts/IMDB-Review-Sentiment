import numpy as np
import pandas as pd
import pickle
from sklearn.linear_model import LogisticRegression
from src.logger import logging
from src.exception import MyException
import sys

def load_data(file_path: str) -> pd.DataFrame:
    """Load data from a CSV file."""
    try:
        df = pd.read_csv(file_path)
        logging.info(f"Data loaded from {file_path}")
        return df
    except Exception as e:
        raise MyException(e, sys) from e

def train_model(X_train: np.ndarray, y_train: np.ndarray) -> LogisticRegression:
    try:
        clf = LogisticRegression(C=1, solver='liblinear', penalty='l2')
        clf.fit(X_train, y_train)
        logging.info("Model training completed.")
        return clf
    except Exception as e:
        raise MyException(e, sys) from e
    
def save_model(model: LogisticRegression, file_path: str) -> None:
    try:
        with open(file_path, 'wb') as file:
            pickle.dump(model, file)
        logging.info(f"Model saved to {file_path}")
    except Exception as e:
        raise MyException(e, sys) from e

def main():
    try:
        train_data = load_data('./data/processed/train_bow.csv')
        X_train = train_data.iloc[:, :-1].values
        y_train = train_data.iloc[:, -1].values

        clf = train_model(X_train, y_train)
        save_model(clf, 'models/model.pkl')
    except Exception as e:
        raise MyException(e, sys) from e

if __name__ == "__main__":
    main()