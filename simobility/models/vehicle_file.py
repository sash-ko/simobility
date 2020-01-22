import json
import numpy as np
import random
import uuid
from shapely.geometry import shape
from ..core.vehicle import Vehicle
from ..core.position import Position


def infleet_geojson(
    clock, fleet, sample_size: int, stations_file: str, geofence=None, seed=None
):
    """
    """

    # np.random.seed(seed)
    state = np.random.RandomState(seed)

    # reproduce vehicle ids
    rd = random.Random()
    rd.seed(seed)

    with open(stations_file) as f:
        stations = json.load(f)

    stations = [s["geometry"] for s in stations["features"]]

    if geofence:
        stations = [s for s in stations if shape(s).within(geofence)]

    for item in state.choice(stations, sample_size):
        lon, lat = item["coordinates"]

        id_ = uuid.UUID(int=rd.getrandbits(128)).hex
        vehicle = Vehicle(clock, vehicle_id=id_)
        fleet.infleet(vehicle, Position(lon, lat))
