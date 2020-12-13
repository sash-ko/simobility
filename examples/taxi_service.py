"""
Implementation of taxi service that operates with following logic:

1. Service find a list of candidate taxies for one booking
2. It sends requests to all candidate taxies
3. The first taxi driver that accepts the request takes the job

"""

from typing import List, Tuple
import random
from collections import defaultdict
from simobility.core import Vehicle
from simobility.core import Booking
from simobility.core.tools import basic_booking_itinerary


class TaxiService:
    def __init__(self, clock, taxi_drivers, dispatcher):
        self.clock = clock
        self.taxi_drivers = taxi_drivers
        self.dispatcher = dispatcher

        self.bookings_queue = []
        self.locked_bookings = []

    def add_booking_request(self, booking: Booking):
        self.bookings_queue.append(booking)

    def step(self):
        taxies = self.find_idling_taxies()
        if self.bookings_queue and taxies:
            # first come, first servce (FIFO)
            booking = self.bookings_queue.pop(0)

            candidates = self.taxi_drivers.find_candidate_taxies(booking, taxies)

            self.locked_bookings.append(booking)

            for taxi in candidates:
                self.taxi_drivers.add_request(taxi, booking)

        accepted = self.taxi_drivers.get_accepted_requests()

        for (taxi, booking) in accepted:
            itinerary = basic_booking_itinerary(self.clock.now, taxi, booking)
            self.dispatcher.dispatch(itinerary)

            self.locked_bookings.remove(booking)

    def find_candidate_taxies(
        self, booking: Booking, taxies: List[Vehicle]
    ) -> List[Vehicle]:
        # take 5 random taxies
        return random.sample(taxies, 5)


class TaxiDrivers:
    def __init__(self, clock, fleet):
        self.clock = clock
        self.fleet = fleet

        self.requests_per_booking = defaultdict(list)
        self.accepted = []

    def add_request(self, taxi: Vehicle, booking: Booking):
        self.requests_per_booking[booking].append(taxi)

    def get_accepted_requests(self) -> List[Tuple[Vehicle, Booking]]:
        return self.accepted

    def find_idling_taxies(self) -> List[Vehicle]:
        """Idling vehicle is a vehicle without an itinerary"""
        vehicles = self.fleet.get_online_vehicles()
        return [v for v in vehicles if self.dispatcher.get_itinerary(v) is None]

    def step(self):
        self.driver_acceptance_model()

        for (taxi, booking) in self.accepted:
            if booking in self.requests_per_booking:
                del self.requests_per_booking[booking]

    def driver_acceptance_model(self):
        for booking, taxies in self.requests_per_booking.items():
            # just an example of a acceptance logic
            # accept now or later with probability 1/5
            if random.randint(0, 5) == 0:
                # randomly choose a taxi - just an example of
                # an acceptance logic
                taxi = random.choice(taxies)
                self.accepted.append((taxi, booking))


def run_simulation(fleet, clock, demand, dispatcher):
    num_steps = 100

    drivers = TaxiDrivers(clock, fleet)
    taxi_service = TaxiService(clock, drivers, dispatcher)

    for i in range(num_steps):

        bookings = demand.next()
        for booking in bookings:
            taxi_service.add_booking_request(booking)

        taxi_service.step()
        drivers.step()

        fleet.step()

        dispatcher.step()

        clock.tick()

