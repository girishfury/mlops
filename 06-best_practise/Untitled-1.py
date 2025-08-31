#!/usr/bin/env python
# coding: utf-8
import os
import warnings
warnings.filterwarnings('ignore')
import sys
import pickle
import pandas as pd
import pyarrow as pa


# INPUT_FILE_PATTERN="s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
OUTPUT_FILE_PATTERN="s3://nyc-duration/out/{year:04d}-{month:02d}.parquet"

def get_input_path(year, month):
    return f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'

def get_output_path(year, month):
    return f'out/{year:04d}-{month:02d}.parquet'  # Key path only (no bucket name prefix)

def read_data(filename):
    return pd.read_parquet(filename)    

def prepare_data(df, categorical):
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')    
    return df


def main(year, month):
    categorical = ['PULocationID', 'DOLocationID']
    bucket_name = 'nyc-duration'
    input_file = get_input_path(year, month)
    output_file = get_output_path(year, month)

    print(f'reading data from {input_file}')
    rd = read_data(input_file)
    df = prepare_data(rd, categorical)
    
    with open('model.bin', 'rb') as f_in:
        dv, lr = pickle.load(f_in)

    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')
    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)
    
    print('predicted mean duration:', y_pred.mean())
    
    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred

    filesystem = pa.fs.S3FileSystem(
    access_key='dummy_key',
    secret_key='dummy_secret',
    endpoint_override='http://localhost:4566'  # Localstack endpoint
    )

    print(f'Writing results to s3://{bucket_name}/{output_file}')
    df_result.to_parquet(f'{bucket_name}/{output_file}', engine='pyarrow', index=False, filesystem=filesystem)


if __name__ == '__main__':
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    main(year, month)