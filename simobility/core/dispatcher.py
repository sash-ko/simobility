from typing import List, Dict, Optional
from .state_transitions import update_next_bookings
from .state_transitions import do_job
from .itinerary import Itinerary
from .vehicle import Vehicle


class Dispatcher:
    """ Simulation controller
    """

    def __init__(self):
        self.itineraries: Dict[Vehicle, Itinerary] = {}

    def set_itinerary(self, itinerary: Itinerary):
        # TODO: itinerary consistency is a "business logic" level

        self.itineraries[itinerary.vehicle] = itinerary

    def get_itinerary(self, vehicle: Vehicle) -> Optional[Itinerary]:
        if vehicle in self.itineraries:
            return self.itineraries[vehicle]
        return None

    def cancel_itinerary(self, vehicle: Vehicle):
        vehicle.stop()
        del self.itineraries[vehicle]

    def step(self, itineraries: List[Itinerary]):
        # TODO: pooling and rebalancing?????

        if itineraries:
            for s in itineraries:
                self.set_itinerary(s)

        # finish current job and start next one

        for vehicle, itinerary in self.itineraries.items():
            # vehicle = self.fleet.get_vehicle(vehicle_id)
            # Run until all jobs are done or started job which can't be
            # finished in 1 round (move_to and wait)

            # The main idea is following: each job can be done in zero time
            # (pickup, dropoff, move to the same location). But some jobs
            # require more time (moving).
            # For example:
            # - time 0
            #   * vehicle is moving to pickup
            #       - eta = 3
            #       - vehicle state changed to "moving_to"
            #   * booking state changed to "waiting_pickup"
            # - time: 1
            # - time: 2
            # - time: 3
            #   * vehicle arrived at pickup location
            #       - vehicle state changed to "idling"
            #       - moving to dropoff
            #       - vehicle state changed to "moving_to"
            #       - eta = 2
            #   * pickup:
            #       - booking state changed to "pickup"
            #       - booking state changed to "waiting_dropoff"
            # - time: 4
            # - time: 5
            #   * vehivle arrived at dropoff location
            #       - vehicle state changed to "idling"
            #       - vehicle is moving to the parking
            #       - vehicle state changed to "moving_to"
            #   * dropoff:
            #       - booking state changed to "pickup"
            #       - booking state changed to "complete"

            do_job(itinerary)
            # update states on the next bookings
            update_next_bookings(itinerary)

        self.itineraries = {
            v: it for v, it in self.itineraries.items()
            if not it.is_completed()
        }
