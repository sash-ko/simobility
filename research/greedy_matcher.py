import sys
import os

sys.path.insert(0, os.path.abspath("../../simobility"))


from typing import List, Tuple, Dict
import numpy as np
import logging
import yaml

import simobility.routers as routers
from simobility.core.tools import basic_booking_itinerary
from simobility.simulator.simulator import Simulator, Context
from simobility.core import Clock
from simobility.core import Itinerary
from simobility.core import Booking
from simobility.core import Vehicle
from simobility.routers.base_router import BaseRouter
from simobility.core.loggers import configure_root, config_state_changes
from simobility.core.metrics import calculate_metrics
from scenario import create_scenario
from metrics import print_metrics


configure_root(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")

log = logging.getLogger("urllib3.connectionpool")
log.setLevel(logging.CRITICAL)


class GreedyMatcher:
    """
    Match bookings in FIFO order -  the oldest booking is processed first.
    Each booking is matched with closest vehicle
    """

    def __init__(self, context: Context, router:BaseRouter, config: Dict):
        self.clock = context.clock
        self.fleet = context.fleet
        self.booking_service = context.booking_service
        self.dispatcher = context.dispatcher

        router = routers.CachingRouter(router)
        self.router = router

        # Search time radius in minutes (max ETA)
        search_radius = config['solvers']['greedy_matcher']['search_radius']
        self.search_radius = self.clock.time_to_clock_time(search_radius, "m")

        logging.info(f"Search radius: {self.search_radius}")

    def step(self) -> List[Itinerary]:
        # bookings in descending order
        bookings = self.booking_service.get_pending_bookings()
        vehicles = self.get_idling_vehicles()

        itineraries = []
        # FIFO
        for booking in bookings:
            if vehicles:
                vehicle, distance = self.closest_vehicle(booking, vehicles)
                if distance > self.search_radius:
                    continue

                vehicles.remove(vehicle)

                itinerary = basic_booking_itinerary(
                    self.clock.now, vehicle, booking, pickup_eta=distance
                )
                itineraries.append(itinerary)

        return itineraries

    def get_idling_vehicles(self) -> List[Vehicle]:
        """Idling vehicle is a vehicle without an itinerary"""
        vehicles = self.fleet.get_online_vehicles()
        return [v for v in vehicles if self.dispatcher.get_itinerary(v) is None]

    def closest_vehicle(
        self, booking: Booking, vehicles: List[Vehicle]
    ) -> Tuple[Vehicle, float]:

        positions = [v.position for v in vehicles]

        # calculate time distance from pickup to all available vehicles
        distances = self.router.calculate_distance_matrix(positions, [booking.pickup])
        distances = distances.ravel()

        # take the closest vehicle
        idx = np.argmin(distances)
        return vehicles[idx], distances[idx]


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

    matcher = GreedyMatcher(context, router, config)

    simulator = Simulator(matcher, context)
    simulator.simulate(demand, config["simulation"]["duration"])

    print_metrics(config["simulation"]["output"], context.clock)
