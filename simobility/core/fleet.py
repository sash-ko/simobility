from typing import List, Type, Dict
import random
import uuid
import numpy as np
import json
from shapely.geometry import shape
from .vehicle_engine import VehicleEngine
from .vehicle import StopReasons, Vehicle
from .clock import Clock
from .position import Position
from ..routers.base_router import BaseRouter
from ..utils import read_polygon


class Fleet:
    def __init__(self, clock: Clock, router: Type[BaseRouter]):
        # vehicle_id -> Vehicle
        self._vehicles: Dict[str, Vehicle] = {}
        self._router = router
        self.clock = clock

    def get_online_vehicles(self) -> List[Vehicle]:
        return [v for v in self._vehicles.values() if not v.is_offline()]

    def infleet(self, vehicle: Vehicle, position: Position):
        engine = create_engine(position, self._router, self.clock)
        vehicle.install_engine(engine)

        self._vehicles[vehicle.id] = vehicle

    def get_vehicle(self, vehicle_id: str) -> Vehicle:
        return self._vehicles[vehicle_id]

    def step(self):
        for v in self._vehicles.values():
            v.step()

    def stop_vehicles(self):
        for v in self._vehicles.values():
            if not v.is_idling():
                v.stop(StopReasons.stop)

    def infleet_from_geojson(
        self, fleet_size: int, stations_file: str, geofence_file=None, seed=None
    ):
        """
        """

        np.random.seed(seed)
        # state = np.random.RandomState(seed)

        # reproduce vehicle ids
        # rd = random.Random()
        # rd.seed(seed)

        with open(stations_file) as f:
            stations = json.load(f)

        stations = [s["geometry"] for s in stations["features"]]

        if geofence_file:
            geofence = read_polygon(geofence_file)
            stations = [s for s in stations if shape(s).within(geofence)]

        for item in state.choice(stations, fleet_size):
            lon, lat = item["coordinates"]

            # id_ = uuid.UUID(int=rd.getrandbits(128)).hex

            id_ = len(self._vehicles) + 1
            vehicle = Vehicle(self.clock, vehicle_id=id_)
            self.infleet(vehicle, Position(lon, lat))


def create_engine(pos: Position, router: Type[BaseRouter], clock: Clock):
    return VehicleEngine(pos, router, clock)
