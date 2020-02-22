from typing import List
import numpy as np
from simobility.simulator.simulator import Context
import simobility.routers as routers
from simobility.core import Itinerary
from simobility.core import Vehicle
from simobility.core.tools import basic_booking_itinerary


class RandomMatcher:
    """
    Match bookings in FIFO order with random vehicles

    simobility requires matchers to implement only one function:

    def step(self) -> List[Itinerary]:
        pass
    
    """

    def __init__(self, context: Context):
        self.clock = context.clock
        self.fleet = context.fleet
        self.booking_service = context.booking_service
        self.dispatcher = context.dispatcher

        router = routers.LinearRouter(self.clock)
        self.router = router

    def step(self) -> List[Itinerary]:
        bookings = self.booking_service.get_pending_bookings()
        vehicles = self.get_idling_vehicles()

        itineraries = []
        for booking in bookings:
            if not vehicles:
                break

            vehicle = np.random.choice(vehicles)
            vehicles.remove(vehicle)

            eta = self.router.estimate_duration(vehicle.position, booking.pickup)
            itinerary = basic_booking_itinerary(
                self.clock.now, vehicle, booking, pickup_eta=eta
            )
            itineraries.append(itinerary)

        return itineraries

    def get_idling_vehicles(self) -> List[Vehicle]:
        """Idling vehicle is a vehicle without an itinerary"""
        vehicles = self.fleet.get_online_vehicles()
        return [v for v in vehicles if self.dispatcher.get_itinerary(v) is None]
