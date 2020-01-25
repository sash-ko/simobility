import logging
import json
import argparse
from shapely.geometry import shape
from shapely.geometry.polygon import Polygon
import geopandas as gpd
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

"""
Preprocess and convert CSV file with historical trip data to feather format.
Preprocessing means removing trips that are outside of geofence and change column
names.

Expected CSV structure:

    "tpep_pickup_datetime": datetime, 
    "tpep_dropoff_datetime": datetime,
    "passenger_count": integer,
    "trip_distance": float,
    "pickup_longitude": float,
    "pickup_latitude": float,
    "dropoff_longitude": float,
    "dropoff_latitude": float

Output file structure:
    "pickup_datetime",
    "dropoff_datetime",
    "passenger_count",
    "distance",
    "pickup_lon",
    "pickup_lat",
    "dropoff_lon",
    "dropoff_lat"

"""


def read_polygon(file_name) -> Polygon:
    """Read polygon fron geojson file and convert to shapely.Geometry"""

    geom = None
    with open(file_name) as f:
        geom = json.load(f)
        geom = shape(geom["features"][0]["geometry"])

    return geom


def read_data(file_name) -> pd.DataFrame:
    """Read trip data from CSV file. Reader assumes certain file structure:
    name and type of columns.

    TODO: allow user to specify column names
    """

    logging.info(f"Reading file {file_name}...")

    data = pd.read_csv(
        file_name,
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

    logging.info(f"Data shape {data.shape}")

    return data


def preprocess(
    data: pd.DataFrame, min_distance: float, max_distance: float
) -> pd.DataFrame:
    """Basic preprocessing:
    - convert distance from miles to km
    - remove trips that are too long or too short
    """

    # miles to km
    data.trip_distance = data.trip_distance * 1.60934

    print(f"Filtering by distance...")
    data = data[
        (data.trip_distance >= min_distance) & (data.trip_distance <= max_distance)
    ]
    print(f"Data shape {data.shape}")

    return data


def filter_by_shape(data: pd.DataFrame, geofence: Polygon) -> pd.DataFrame:
    """Remove trips outside of geofence. Filter by pickup and dropoff locations"""

    logging.info("Creating pickup geometry...")

    pickup_data = gpd.GeoDataFrame(
        data,
        geometry=gpd.points_from_xy(data["pickup_longitude"], data["pickup_latitude"]),
    )

    logging.info("Filtering by pickups...")
    data = data[pickup_data.geometry.within(geofence)]

    logging.info("Creating dropoff geometry...")
    dropoff_data = gpd.GeoDataFrame(
        data,
        geometry=gpd.points_from_xy(
            data["dropoff_longitude"], data["dropoff_latitude"]
        ),
    )

    logging.info("Filtering by dropoffs...")
    data = data[dropoff_data.geometry.within(geofence)]

    logging.info(f"Data shape {data.shape}")
    return data.drop(["geometry"], axis=1)


def save_to_feather(data, output_file):
    """Use feather format to store preprocessed trip data

    Best format to save pandas data
    https://towardsdatascience.com/the-best-format-to-save-pandas-data-414dca023e0d
    """
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

    logging.info(f"Saving to {output_file}...")

    data.reset_index(drop=True).to_feather(output_file)


# TODO: file name as parameter
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess data")
    parser.add_argument("--data-file", help="Input CSV file")
    parser.add_argument("--output-file", help='File with results in "feather" format')
    parser.add_argument("--geofence-file", help="GeoJSON file")
    parser.add_argument("--min-distance", type=int, default=0.2, help="Distance in km")
    parser.add_argument("--max-distance", type=int, default=20, help="Distance in km")

    args = parser.parse_args()

    data = read_data(args.data_file)
    data = preprocess(data, args.min_distance, args.max_distance)

    geofence = read_polygon(args.geofence_file)
    data = filter_by_shape(data, geofence)

    save_to_feather(data, args.output_file)
