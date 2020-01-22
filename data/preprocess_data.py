import json
import argparse
from shapely.geometry import shape
from shapely.geometry.polygon import Polygon
# import shapely.geometry as geometry
import geopandas as gpd
import pandas as pd
from haversine import haversine

# minimum distance between pickup and dropoff (km)
MIN_DISTANCE = 0.2
MAX_DISTANCE = 20


def read_geofence(file_name) -> Polygon:
    geofence = None
    with open(file_name) as f:
        geofence = json.load(f)
        geofence = shape(geofence["features"][0]["geometry"])
    return geofence


def read_data(file_name) -> pd.DataFrame:
    print(f'Reading file {file_name}...')

    data = pd.read_csv(
        "yellow_feb_1w_trips.csv",
        usecols=[
            "tpep_pickup_datetime",
            "tpep_dropoff_datetime",
            "passenger_count",
            "trip_distance",
            "pickup_longitude",
            "pickup_latitude",
            "dropoff_longitude",
            "dropoff_latitude",
        ],
        parse_dates=["tpep_pickup_datetime", "tpep_dropoff_datetime"],
    )

    print(f"Data shape {data.shape}")

    return data


def preprocess(data: pd.DataFrame) -> pd.DataFrame:
    # miles to km
    data.trip_distance = data.trip_distance * 1.60934

    print(f"Filtering by distance...")
    data = data[
        (data.trip_distance > MIN_DISTANCE) & (data.trip_distance < MAX_DISTANCE)
    ]
    print(f"Data shape {data.shape}")

    return data


def filter_by_shape(data: pd.DataFrame, geofence: Polygon) -> pd.DataFrame:
    print("Creating pickup geometry...")
    pickup_data = gpd.GeoDataFrame(
        data,
        geometry=gpd.points_from_xy(data["pickup_longitude"], data["pickup_latitude"]),
    )

    print("Filtering by pickups...")
    data = data[pickup_data.geometry.within(geofence)]

    print("Creating dropoff geometry...")
    dropoff_data = gpd.GeoDataFrame(
        data,
        geometry=gpd.points_from_xy(
            data["dropoff_longitude"], data["dropoff_latitude"]
        ),
    )

    print("Filtering by dropoffs...")
    data = data[dropoff_data.geometry.within(geofence)]

    print(f"Data shape {data.shape}")
    return data.drop(["geometry"], axis=1)


def save_to_feather(data, output_file):
    columns = [
        "pickup_datetime",
        "dropoff_datetime",
        "passenger_count",
        "distance",
        "pickup_lon",
        "pickup_lat",
        "dropoff_lon",
        "dropoff_lat",
    ]

    data.columns = columns

    print(f'Saving to {output_file}...')

    # Best format to save pandas data
    # https://towardsdatascience.com/the-best-format-to-save-pandas-data-414dca023e0d
    data.reset_index(drop=True).to_feather(output_file)


# TODO: file name as parameter
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess data")
    parser.add_argument("--data-file", help="Input CSV file")
    parser.add_argument("--output-file", help='File with results in "feather" format')
    parser.add_argument("--geofence-file", help="GeoJSON file")

    args = parser.parse_args()

    data = read_data(args.data_file)
    data = preprocess(data)

    geofence = read_geofence(args.geofence_file)
    data = filter_by_shape(data, geofence)

    save_to_feather(data, args.output_file)
