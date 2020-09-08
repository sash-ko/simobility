import logging
from dataclasses import dataclass
from simobility.core import Fleet
from simobility.core import BookingService
from simobility.core import Dispatcher
from simobility.core.clock import Clock


@dataclass
class Context:
    """Required simulation entities"""

    clock: Clock
    fleet: Fleet
    booking_service: BookingService
    dispatcher: Dispatcher


class Simulator:
    """ Simulator connects all simulation building blocks. It runs
    a simulation step-by-step by calling step() function of each of the
    entities in a specific order.

    NOTE: It is importance to call step() functions in a specific order and the
    main and only role of this class is to demontrate how to do it. So the class
    on itself is not required for running simulations. For more details, see examples
    """

    def __init__(self, matcher, context: Context):
        self.clock = context.clock
        self.matcher = matcher
        self.fleet = context.fleet
        self.booking_service = context.booking_service
        self.dispatcher = context.dispatcher

    def simulate(self, demand, duration_mins: int):
        """
        Parameters
        ----------

        demand : object
            Any object that implements next() method. The method should return a list
            of Booking instances

        duration_mins : int
            Real world time of a simulation. The time will be converted into the internal
            simulated time which is used as the number of simulation steps
            
        """
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
            for it in itineraries:
                self.dispatcher.dispatch(it)

            # change booking state to matched and waiting for pickup or dropoff
            # ask vehicles to move
            self.dispatcher.step()

            self.clock.tick()

        self.fleet.stop_vehicles()
