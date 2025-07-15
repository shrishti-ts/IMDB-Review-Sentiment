import numpy as np
import pandas as pd
import os
import sys
import re
import nltk
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from src.logger import logging
from src.exception import MyException
nltk.download('wordnet')
nltk.download('stopwords')

def preprocess_dataframe(df: pd.DataFrame, col: str = "text") -> pd.DataFrame:
    """
    Preprocess a DataFrame by applying test preprocessing to a specific column.

    Args
    ----
        df (pd.DataFrame): The dataframe to preprocess.
        col (str): The name  of the column containing text.
    Returns
    -------
        pd.DataFrame: The preprocessed DataFrame.
    """ 
    # Initialize lemmatizer and stopwords
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))

    def preprocess_text(text: str) -> str:
        """Helper function to preprocess a single text string."""
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        # Remove numbers
        text = ''.join([char for char in text if not char.isdigit()])
        # Convert to lowercase
        text = text.lower()
        # Remove punctuations
        text = re.sub('[%s]' % re.escape(string.punctuation), ' ', text)
        text = text.replace('؛', "")
        text = re.sub('\s+', ' ', text).strip()
        # Remove stop words
        text = " ".join([word for word in text.split() if word not in stop_words])
        # Lemmatization
        text = " ".join([lemmatizer.lemmatize(word) for word in text.split()])
        return text

    df[col] = df[col].apply(preprocess_text)

    df = df.dropna(subset=[col])
    logging.info("Data pre-processing completed.")
    return df

def main():
    try:
        # fetch the data
        train_data = pd.read_csv('./data/raw/train.csv')
        test_data = pd.read_csv('./data/raw/test.csv')

        # Transform the data
        train_processed_data = preprocess_dataframe(train_data, 'review')
        test_processed_data = preprocess_dataframe(test_data, 'review')

        # Store the data inside data/processed
        data_path = os.path.join("./data", "interim")
        os.makedirs(data_path, exist_ok=True)

        train_processed_data.to_csv(os.path.join(data_path, "train_processed.csv"), index=False)
        test_processed_data.to_csv(os.path.join(data_path, "test_processed.csv"), index=False)

        logging.info(f"Processed data saved to {data_path}")
    except Exception as e:
        raise MyException(e, sys) from e
    
if __name__ == "__main__":
    main()