import boto3
import os
import sys
import pandas as pd
import logging
from src.logger import logging
from src.exception import MyException
from io import StringIO

logging.getLogger("boto3").setLevel(logging.ERROR)
logging.getLogger("botocore").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

class s3_operations:
    def __init__(self, bucket_name: str, aws_access_key_id: str, aws_secret_access_key: str, region_name: str="us-east-1"):
        """
        Initializes the s3_operation class with AWS credentials and s3 bucket details.
        """
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        logging.info("Data Ingestion from S3 bucket initialized.")
    
    def fetch_file_from_s3(self, file_key: str) -> pd.DataFrame:
        """
        Fetches a CSV file from the s3 bucket and returns it as Pandas Dataframe.

        :param file_key: S3 file path
        :return: Pandas DataFrame
        """
        try:
            logging.info(f"Fetching file '{file_key}' from S3 bucket '{self.bucket_name}'...")
            obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            df = pd.read_csv(StringIO(obj['Body'].read().decode('utf-8')))
            logging.info(f"Successfully fetched and loaded '{file_key}' from S3 that has {len(df)} records.")
            return df
        except Exception as e:
            raise MyException(e, sys) from e

# Example usage
if __name__ == "__main__":
    BUCKET_NAME = "review-analysis-project"
    FILE_KEY = "data.csv"
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    data_ingestion = s3_operations(BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    
    df = data_ingestion.fetch_file_from_s3(FILE_KEY)

    if df is not None:
        print(f"Data fetched with {len(df)} records...")