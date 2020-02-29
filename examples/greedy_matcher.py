from typing import List, Tuple, Dict
import numpy as np
import logging

import simobility.routers as routers
from simobility.core.tools import basic_booking_itinerary
from simobility.simulator.simulator import Context
from simobility.core import Itinerary
from simobility.core import Booking
from simobility.core import Vehicle
from simobility.routers.base_router import BaseRouter


class GreedyMatcher:
    """
    Match bookings in FIFO order -  the oldest booking is processed first.
    Each booking is matched with closest vehicle
    """

    def __init__(self, context: Context, router: BaseRouter, config: Dict):
        self.clock = context.clock
        self.fleet = context.fleet
        self.booking_service = context.booking_service
        self.dispatcher = context.dispatcher

        # cache routes
        router = routers.CachingRouter(router)
        self.router = router

        # Search time radius in minutes (max ETA)
        search_radius = config["solvers"]["greedy_matcher"]["search_radius"]
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
                vehicle, eta = self.closest_vehicle(booking, vehicles)
                if eta > self.search_radius:
                    continue

                vehicles.remove(vehicle)

                itinerary = basic_booking_itinerary(self.clock.now, vehicle, booking)
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

