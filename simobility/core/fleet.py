from typing import List, Type, Dict
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
    """ Keeps all online and offline vehicles in one place. Creates 
    an engine for each vehicle using a router. This router tells vehicles
    how to move in a simulated world.
    """

    def __init__(self, clock: Clock, router: Type[BaseRouter]):
        # {vehicle_id: Vehicle}
        self._vehicles: Dict[str, Vehicle] = {}
        self._router = router
        self.clock = clock

    def get_online_vehicles(self) -> List[Vehicle]:
        """Return vehicles that are currently active (have status not offile)"""

        return [v for v in self._vehicles.values() if not v.is_offline()]

    def infleet(self, vehicle: Vehicle, position: Position):
        """Add a new vehicle to the fleet and put it at a particular location
        in the simulater world."""

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
        self,
        fleet_size: int,
        stations_file: str,
        geofence_file: str = None,
        seed: int = None,
    ):
        """Reads json file with points (stations) and creates new vehicles at each
        of the points. If `geofence_file` is specidied use polygon from that file as
        a geofence - ignore all vehicles outsize of the area

        Parameters
        ----------

        fleet_size : int
            The number of vehicles to infleet by positioning on stations from the file

        stations_file : str
            The name of the geojson file with stations

        geofence_file : str
            The name of a geojson file with geofence polygon

        seed : int
            Seed vehicle positioning
        """
        with open(stations_file) as f:
            stations = json.load(f)

        stations = [s["geometry"] for s in stations["features"]]

        if geofence_file:
            geofence = read_polygon(geofence_file)
            stations = [s for s in stations if shape(s).within(geofence)]

        # Use local seed - infleet vehicles independenlty from other parts
        # of the system
        state = np.random.RandomState(seed)

        for item in state.choice(stations, fleet_size):
            lon, lat = item["coordinates"]

            vehicle = Vehicle(self.clock)
            self.infleet(vehicle, Position(lon, lat))


def create_engine(
    pos: Position, router: Type[BaseRouter], clock: Clock
) -> VehicleEngine:
    return VehicleEngine(pos, router, clock)
