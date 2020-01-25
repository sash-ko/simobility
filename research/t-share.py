import sys
import os

sys.path.insert(0, os.path.abspath("../../simobility"))

import yaml
import numpy as np
from h3 import h3
from shapely.geometry import shape, mapping
import logging
from math import ceil
from typing import Dict, List, Set
from collections import defaultdict

from simobility.core.tools import basic_booking_itinerary
import simobility.routers as routers
from simobility.core import Clock
from simobility.core import Position
from simobility.core import Itinerary
from simobility.core import Vehicle
from simobility.routers.base_router import BaseRouter
from simobility.core import Fleet
from simobility.simulator.simulator import Simulator, Context
from simobility.core import BookingService, Dispatcher
from simobility.core.loggers import configure_root, config_state_changes
from simobility.utils import read_polygon

from scenario import create_scenario
from metrics import print_metrics


configure_root(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")

log = logging.getLogger("urllib3.connectionpool")
log.setLevel(logging.CRITICAL)


class CityGrid:
    def __init__(self, geom: Dict, router: BaseRouter, resolution: int = 7):
        hexagons = h3.polyfill(geom, resolution)
        self.hexagons = list(hexagons)
        self.resolution = resolution

        self.router = router

    def create_index(self, max_time_radius, max_dist_radius):
        origins = [Position(*h3.h3_to_geo(h)) for h in self.hexagons]
        destinations = origins[:]

        # destinations = [h3.h3_to_geo(h) for h in self.hexagons]

        travel_time = self.router.calculate_distance_matrix(origins, destinations)

        hexagons = np.array(self.hexagons)

        self.temporal_index = {}

        for hex_i, hex_indices in enumerate(np.argsort(travel_time)):
            self.temporal_index[hexagons[hex_i]] = {
                hexagons[idx]: travel_time[hex_i][idx]
                for idx in hex_indices
                if travel_time[hex_i][idx] < max_time_radius and hex_i != idx
            }

        distances = self.router.calculate_distance_matrix(origins, destinations, False)

        self.spatial_index = {}

        for hex_i, hex_indices in enumerate(np.argsort(distances)):
            self.spatial_index[hexagons[hex_i]] = {
                hexagons[idx]: distances[hex_i][idx]
                for idx in hex_indices
                if distances[hex_i][idx] < max_dist_radius and hex_i != idx
            }

    def find_neighbours(self, hexagon: str, travel_time=None) -> List:
        neighbours = []

        for h, t in self.temporal_index[hexagon].items():
            if travel_time is not None:
                if t <= travel_time:
                    neighbours.append((h, t))
            else:
                neighbours.append((h, t))
        return neighbours

    def find_hex(self, position: Position) -> str:
        lon, lat = position.coords
        h3_address = h3.geo_to_h3(lon, lat, self.resolution)

        if h3_address not in self.spatial_index:
            h3_address = None
        return h3_address


# TODO: use "area" or something like this instead of hexagon
class Matcher:
    def __init__(self, city_grid: CityGrid, router, context: Context):
        self.city_grid = city_grid
        self.clock = context.clock
        self.fleet = context.fleet
        self.booking_service = context.booking_service
        self.dispatcher = context.dispatcher
        self.router = router

        # max travel time in minutes
        # self.search_radius = 5

        # self.search_radius = ceil(
        #     self.clock.time_to_clock_time(self.search_radius, "m")
        # )

        # used to calculate pickup window
        self.max_waiting_time = 5
        self.max_waiting_time = ceil(
            self.clock.time_to_clock_time(self.max_waiting_time, "m")
        )

        # hexagon - vehicle - eta
        self.hex_vehicles = defaultdict(defaultdict)

        self._position_vehicles()

    def _position_vehicles(self):
        vehicles = self.fleet.get_online_vehicles()
        for v in vehicles:
            hexagon = self.city_grid.find_hex(v.position)
            if hexagon:
                self.hex_vehicles[hexagon][v] = self.clock.now

    def step(self) -> List[Itinerary]:
        itineraries = []

        bookings = self.booking_service.get_pending_bookings()

        assigned = set()
        for booking in bookings:
            # pickup window
            max_pickup_time = booking.created_at + self.max_waiting_time

            candidates = self.find_candidate_vehicles(
                booking.pickup, max_pickup_time, assigned
            )

            if candidates:
                candidates.sort(key=lambda item: item[-1])
                hexagon, vehicle, eta = candidates[0]

                itinerary = basic_booking_itinerary(
                    self.clock.now, vehicle, booking, pickup_eta=eta
                )
                itineraries.append(itinerary)

                del self.hex_vehicles[hexagon][vehicle]

                hexagon = self.city_grid.find_hex(booking.dropoff)
                self.hex_vehicles[hexagon][vehicle] = eta

                assigned.add(vehicle)

        return itineraries

    def find_candidate_vehicles(self, pickup: Position, max_pickup_time: int, ignore_vehicles: Set[Vehicle]):
        candidates = []

        hexagon = self.city_grid.find_hex(pickup)
        if hexagon:
            neighbours = self.city_grid.find_neighbours(hexagon)

            for n, t in neighbours:
                vehicles = self.hex_vehicles[n]
                # TODO: eta can be calculated using router more precisely
                for v, eta in sorted(vehicles.items(), key=lambda item: item[-1]):

                    # TODO: reassign vehicle that are about to finish current trip
                    # TODO: ride sharing
                    if self.dispatcher.get_itinerary(v) is not None:
                        continue

                    if v in ignore_vehicles:
                        continue

                    if eta + t <= max_pickup_time:
                        eta = max(eta, self.clock.now)
                        candidates.append((n, v, eta + t))
        return candidates


if __name__ == "__main__":

    with open("nyc_config.yaml") as cfg:
        config = yaml.load(cfg, Loader=yaml.FullLoader)

    config_state_changes(config["simulation"]["output"])

    context, demand = create_scenario(config)

    if config['solvers']['greedy_matcher']['router'] == 'linear':
        router = routers.LinearRouter(context.clock, config['routers']['linear']['speed'])
    elif config['solvers']['greedy_matcher']['router'] == 'osrm':
        router = routers.OSRMRouter(clock=clock, server=config['routers']['osrm']['server'])
    else:
        raise Exception('Unknown router')

    logging.info(f"Matcher router {router}")

    geofence = read_polygon(config.get("geofence"))
    geofence = mapping(geofence)
    grid = CityGrid(geofence, router, config["simulation"]["resolution"])

    max_time_radius = config['solvers']['tshare_matcher']['max_time_radius']
    max_time_radius = context.clock.time_to_clock_time(max_time_radius, "m")
    max_dist_radius = config['solvers']['tshare_matcher']['max_dist_radius']

    grid.create_index(max_time_radius, max_dist_radius)

    np.random.seed(3424)
    matcher = Matcher(grid, router, context)

    simulator = Simulator(matcher, context)
    simulator.simulate(demand, config["simulation"]["duration"])

    print_metrics(config["simulation"]["output"], context.clock)
