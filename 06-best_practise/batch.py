#!/usr/bin/env python
# coding: utf-8
import warnings
warnings.filterwarnings('ignore')
import sys
import pickle
import pandas as pd
import pyarrow.fs  # Correctly import pyarrow filesystem module
import pyarrow.parquet as pq  # Correctly import pyarrow.parquet for parquet I/O

# Buckets and File Paths (S3)
BUCKET_NAME = 'nyc-duration'
INPUT_FILE_PATTERN = f"s3://{BUCKET_NAME}/in/{{year:04d}}-{{month:02d}}.parquet"
OUTPUT_FILE_PATTERN = f"s3://{BUCKET_NAME}/out/{{year:04d}}-{{month:02d}}.parquet"

def read_data(year, month, filesystem):
    """
    Reads a Parquet file stored in S3 (Localstack) using PyArrow filesystem and converts it to Pandas DataFrame.
    """
    input_file = f"in/{year:04d}-{month:02d}.parquet"  # Relative path in S3
    print(f"Reading data from s3://{BUCKET_NAME}/{input_file}")
    table = pq.read_table(f"{BUCKET_NAME}/{input_file}", filesystem=filesystem)  # Read file from S3
    return table.to_pandas()  # Convert PyArrow Table to Pandas DataFrame

def get_output_path(year, month):
    """
    Dynamically generates the path for saving output results to S3.
    """
    return f"out/{year:04d}-{month:02d}.parquet"  # Relative S3 key path for output

def prepare_data(df, categorical):
    """
    Filters and prepares data by processing trip duration and categorical columns.
    """
    # Add duration column as difference between dropoff and pickup times
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df['duration'].dt.total_seconds() / 60  # Convert duration to minutes

    # Filter durations (keep 1 <= duration <= 60 mins)
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    # Fill missing categorical values with -1, then convert to strings
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    return df

def main(year, month):
    categorical = ['PULocationID', 'DOLocationID']

    # Configure PyArrow S3 filesystem for Localstack
    filesystem = pyarrow.fs.S3FileSystem(
        access_key='dummy_key',
        secret_key='dummy_secret',
        endpoint_override='http://localhost:4566'  # Localstack endpoint
    )

    # Step 1: Read the input data from S3 (Localstack)
    df = read_data(year, month, filesystem)

    # Step 2: Prepare the data
    df = prepare_data(df, categorical)

    # Step 3: Load the pickled ML model and make predictions
    with open('model.bin', 'rb') as f_in:
        dv, lr_model = pickle.load(f_in)

    df['ride_id'] = f"{year:04d}/{month:02d}_" + df.index.astype('str')
    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr_model.predict(X_val)
    print(f"Predicted mean duration: {y_pred.mean():.2f}")
    print(f"Sum of predicted duration: {y_pred.sum():.2f}")

    # Step 4: Save the predictions to S3
    df_result = pd.DataFrame({
        "ride_id": df['ride_id'],
        "predicted_duration": y_pred
    })
    output_file = get_output_path(year, month)  # Relative output key
    print(f"Writing results to s3://{BUCKET_NAME}/{output_file}")
    df_result.to_parquet(
        f"{BUCKET_NAME}/{output_file}",
        engine="pyarrow",
        index=False,
        filesystem=filesystem
    )

if __name__ == '__main__':
    # Pass year and month as script arguments
    year = int(sys.argv[1])  # Example: 2023
    month = int(sys.argv[2])  # Example: 04
    main(year, month)