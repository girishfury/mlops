import sys
import os
import pickle
import pandas as pd
import numpy as np

year = int(sys.argv[1]) #2023
month = int(sys.argv[2])  #3
filename = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet"
output_file = 'output.parquet'

print (f'Prcessing the script with year: {year} and month: {month} file {filename}')

categorical = ['PULocationID', 'DOLocationID']

def read_data(filename):
    print (f'Reading data from {filename}')
    df = pd.read_parquet(filename)    
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')    
    return df

with open('model.bin', 'rb') as f_in:
    dv, model = pickle.load(f_in)

df = read_data(filename)
dicts = df[categorical].to_dict(orient='records')
X_val = dv.transform(dicts)
y_pred = model.predict(X_val)


std_dev = np.std(y_pred)
print(f"The standard deviation of the predicted duration is: {std_dev}")
mean_predicted_duration = round(np.mean(y_pred), 2)  # Calculate mean
print(f"Mean Predicted Duration: {mean_predicted_duration}")