from typing import List, Dict
from .booking import Booking
from .clock import Clock


class BookingService:
    """ BookingService manages all booking requests that enter a simulation
    from a demand model. Each new booking must be in pending state. After
    a booking changes its state to any other state it will be removed from the 
    booking service
    """

    def __init__(self, clock: Clock, max_pending_time: int):
        """
        Parameters
        ----------

        clock : Clock
            Simulated time tracker

        max_pending_time : int
            Maximum time a booking can spend in the queue before the service changes
            booking's state to expired and removes from the queue
        """
        self._pending_bookings: Dict[str, Booking] = {}
        self._max_pending_time = max_pending_time
        self.clock = clock

    def add_booking(self, booking: Booking):
        if not booking.is_pending():
            raise Exception("Booking state is not CREATED")

        self._pending_bookings[booking.id] = booking

    def add_bookings(self, bookings: List[Booking]):
        for booking in bookings:
            self.add_booking(booking)

    def get_pending_bookings(self) -> List[Booking]:
        return list(self._pending_bookings.values())

    def step(self):
        # collected booking that are not in pending state and will be
        # removed from the queue
        non_pending = []

        now = self.clock.clock_time
        for booking in self._pending_bookings.values():
            if not booking.is_pending():
                non_pending.append(booking.id)

            else:
                created = booking.created_at

                # check bookings expiration time
                if (created is not None and (created + self._max_pending_time) < now):
                    booking.set_expired()
                    non_pending.append(booking.id)

        # delete non pending bookings
        for id_ in non_pending:
            del self._pending_bookings[id_]
