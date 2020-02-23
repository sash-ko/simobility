import logging
import pandas as pd
import numpy as np
from datetime import datetime
import uuid
import random

from .itinerary import Itinerary
from .vehicle import Vehicle
from .booking import Booking
from .position import Position


def basic_booking_itinerary(
    current_time: int,
    vehicle: Vehicle,
    booking: Booking,
    pickup_eta: int = None,
    dropoff_eta: int = None,
) -> Itinerary:
    """
    Create a simple Itinerary: one vehicle picks up and drops off
    one customer
    """

    itinerary = Itinerary(current_time, vehicle)

    itinerary.move_to(booking.pickup, pickup_eta)
    itinerary.pickup(booking, pickup_eta)

    itinerary.move_to(booking.dropoff, dropoff_eta)
    itinerary.dropoff(booking, dropoff_eta)

    return itinerary


class ReplayDemand:
    def __init__(
        self,
        clock,
        file_name: str,
        from_datetime: datetime,
        to_datetime: datetime,
        round_to: str,
        sample_size: int = None,
        map_matcher=None,
        seed=None,
    ):
        """
        Expected columns:
        - datetime
        - pickup_lon
        - pickup_lat
        - dropoff_lon
        - dropoff_lat
        """

        self.clock = clock
        self.data = pd.read_feather(file_name)

        logging.debug(f"Total number of trips: {self.data.shape[0]}")

        # # TODO: is it really needed???
        # time_jitter = np.array([
        #     pd.to_timedelta("{} sec".format(np.round(i)))
        #     for i in np.random.normal(0, 120, self.data.datetime.shape[0])
        # ])
        # self.data.datetime = self.data.datetime.dt.to_pydatetime() + time_jitter

        idx = (self.data.pickup_datetime >= from_datetime) & (
            self.data.pickup_datetime < to_datetime
        )
        self.data = self.data[idx]

        logging.debug(f"Time filtered number of trips: {self.data.shape[0]}")

        # "local" randomizer, independent from the "global", simulation level
        state = np.random.RandomState(seed)

        if sample_size is not None:
            replace = self.data.index.shape[0] < sample_size
            index = state.choice(self.data.index, sample_size, replace=replace)
            self.data = self.data.loc[index]

        logging.debug(f"Sample size: {self.data.shape[0]}")

        self.data.pickup_datetime = self.data.pickup_datetime.dt.round(round_to)

        self.demand = {
            g: item for g, item in self.data.groupby(self.data.pickup_datetime)
        }
        self.map_matcher = map_matcher

    def next(self, key=None):
        if key is None:
            key = pd.to_datetime(self.clock.to_datetime())

        bookings = []
        seats = 1

        if key in self.demand:
            for b in self.demand[key].itertuples():
                pu = Position(b.pickup_lon, b.pickup_lat)
                do = Position(b.dropoff_lon, b.dropoff_lat)

                if self.map_matcher:
                    original_pu = pu
                    original_do = do
                    pu = self.map_matcher.map_match(pu)

                    if pu.distance(original_pu) > 0.05:
                        logging.warning(
                            f"Map matched pickup is {pu.distance(original_pu)} away for the original"
                        )
                        # skip booking
                        continue

                    do = self.map_matcher.map_match(do)
                    if do.distance(original_do) > 0.05:
                        logging.warning(
                            f"Map matched dropoff is {do.distance(original_do)} away for the original"
                        )
                        # skip booking
                        continue

                # TODO: move distance thresholds to config
                if pu.distance(do) < 0.1:
                    # logging.warning(f"Pickup and dropoff are too close to each other {pu.distance(do)}")
                    continue

                bookings.append(Booking(self.clock, pu, do, seats))

        return bookings
