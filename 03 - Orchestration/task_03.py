import os
import json
import pandas as pd
import mlflow
from mlflow.tracking import MlflowClient
from prefect import flow, get_run_logger, task
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression

EXPERIMENT_NAME = "prefect-mlflow-experiment"
MODEL_NAME = "prefect-mlflow-model"
TRACKING_URI = "http://127.0.0.1:5000"
file = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-03.parquet'

@task
def read_data(file=file):
    logger = get_run_logger()
    df = pd.read_parquet(file)
    num_records = df.shape[0]
    print(f"Number of records loaded: {num_records}")
    logger.info(f"Number of records loaded: {num_records}")
    return df

@task
def filter_data(df):
    logger = get_run_logger()
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)]
    num_filtered_records = df.shape[0]
    print(f"Number of records after filtering: {num_filtered_records}")
    logger.info(f"Number of records after filtering: {num_filtered_records}")        
    return df

@task
def train_model(df):
    logger = get_run_logger()
    logger.info("Starting model training")    
    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)
    train_dicts = df[categorical].to_dict(orient='records')
    dv = DictVectorizer()
    X_train = dv.fit_transform(train_dicts)
    y_train = df['duration'].values
    model = LinearRegression()
    model.fit(X_train, y_train)
    logger.info("Model trained successfully")
    logger.info(f"Intercept of model (separate): {model.intercept_}")
    print(f"Intercept of model (separate): {model.intercept_}")
    return dv, model


@task
def register_model (model):
    logger = get_run_logger()
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run() as run:
       mlflow.sklearn.log_model(model, artifact_path="pipeline" , registered_model_name=MODEL_NAME)     


@flow
def start_pipeline():
    df = read_data()
    filtered_df = filter_data(df)
    dv, model = train_model(filtered_df)
    register_model(model)

if __name__ == "__main__":
    start_pipeline()
