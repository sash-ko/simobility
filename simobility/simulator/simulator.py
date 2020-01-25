import logging
from dataclasses import dataclass
from simobility.core import Fleet
from simobility.core import BookingService
from simobility.core import Dispatcher
from simobility.core.clock import Clock


@dataclass
class Context:
    clock: Clock
    fleet: Fleet
    booking_service: BookingService
    dispatcher: Dispatcher


class Simulator:
    def __init__(self, matcher, context: Context):
        self.clock = context.clock
        self.matcher = matcher
        self.fleet = context.fleet
        self.booking_service = context.booking_service
        self.dispatcher = context.dispatcher

    def simulate(self, demand, duration_mins):
        num_steps = self.clock.time_to_clock_time(duration_mins, "m")
        logging.info(f"Number of simulation steps: {num_steps}")

        for i in range(num_steps):

            bookings = demand.next()
            self.booking_service.add_bookings(bookings)

            # change booking state to pending
            self.booking_service.step()

            # update vehicle states
            self.fleet.step()

            # match pending bookings and create itineraries
            itineraries = self.matcher.step()
            # itineraries = customer.filter(itineraries)

            # change booking state to matched and waiting for pickup or dropoff
            # ask vehicles to move
            self.dispatcher.step(itineraries)

            self.clock.tick()

        self.fleet.stop_vehicles()
