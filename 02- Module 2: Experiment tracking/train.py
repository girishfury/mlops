import os
import pickle
import click
import mlflow
import mlflow.sklearn

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error


def load_pickle(filename: str):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


@click.command()
@click.option(
    "--data_path",
    default="./output",
    help="Location where the processed NYC taxi trip data was saved"
)
def run_train(data_path: str):

    X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
    X_val, y_val = load_pickle(os.path.join(data_path, "val.pkl"))
    with mlflow.start_run():
        rf = RandomForestRegressor(max_depth=10, random_state=0)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_val)
        rmse = root_mean_squared_error(y_val, y_pred)
        print("RMSE:", rmse)
        # ✅ Log params, metric, and model manually
        mlflow.log_param("max_depth", 10)
        mlflow.log_param("random_state", 0)
        mlflow.log_param("min_samples_split", rf.min_samples_split)
        mlflow.log_metric("rmse", rmse)
        mlflow.sklearn.log_model(rf, "Girish")


if __name__ == '__main__':
    run_train()