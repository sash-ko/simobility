from typing import List, Dict
from .booking import Booking
from .clock import Clock


class BookingService:
    """
    Stores pending bookings. Bookings will be expired after `max_pending_time`
    """

    def __init__(self, clock: Clock, max_pending_time: int):
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
        # TODO: should this be part of the dispatcher????
        non_pending = []

        now = self.clock.clock_time
        for booking in self._pending_bookings.values():
            if not booking.is_pending():
                non_pending.append(booking.id)

            else:
                created = booking.created_at

                if (created is not None and (created + self._max_pending_time) < now):
                    booking.set_expired()
                    non_pending.append(booking.id)

        for id_ in non_pending:
            del self._pending_bookings[id_]
