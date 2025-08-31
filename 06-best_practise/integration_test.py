import pandas as pd
from datetime import datetime
from batch import prepare_data
import pyarrow.fs  # Correctly import pyarrow filesystem module
import pyarrow.parquet as pq  # Correctly import pyarrow.parquet for parquet I/O

BUCKET_NAME = 'nyc-duration'

def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)

def test_prepare_data():
    # Input DataFrame
    data = [
        (None, None, dt(1, 1), dt(1, 10)),      
        (1, 1, dt(1, 2), dt(1, 10)),           
        (1, None, dt(1, 2, 0), dt(1, 2, 59)),  
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),      
    ]
    columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    return pd.DataFrame(data, columns=columns)

def save_parquet():
    filesystem = pyarrow.fs.S3FileSystem(
        access_key='dummy_key',
        secret_key='dummy_secret',
        endpoint_override='http://localhost:4566'  # Localstack endpoint
    )

    df = test_prepare_data()
    file_name = "2023-01.parquet"  # Specify the file name
    s3_path = f"{BUCKET_NAME}/in/{file_name}"
    print(f"Writing results to {s3_path}")
    df.to_parquet(
        s3_path,
        engine="pyarrow",
        index=False,
        filesystem=filesystem
    )
    print(f"File {file_name} saved successfully on S3!")

if __name__ == "__main__":
    save_parquet()
    
