import logging
import pandas as pd
import numpy as np
from datetime import datetime
import uuid
import random

from ..core.position import Position
from ..core.booking import Booking


class DemandFileReplay:
    def __init__(
        self,
        clock,
        file_name: str,
        from_datetime: datetime,
        to_datetime: datetime,
        round_to: str,
        sample_size: int = None,
        seed=None,
        geofence=None,
        map_matcher=None,
    ):
        """

        Expects columns:
        - datetime
        - pickup_lon
        - pickup_lat
        - dropoff_lon
        - dropoff_lat
        """

        # "local" randomizer, independent from the "global", simulation level
        state = np.random.RandomState(seed)

        # seed UUIDs
        self.rd = random.Random()
        self.rd.seed(seed)

        self.clock = clock
        self.data = pd.read_feather(file_name)

        logging.debug(f"Total number of trips: {self.data.shape[0]}")

        # self.data.columns = list(columns.keys())

        # # TODO: is it really needed???
        # time_jitter = np.array([
        #     pd.to_timedelta("{} sec".format(np.round(i)))
        #     for i in np.random.normal(0, 120, self.data.datetime.shape[0])
        # ])
        # self.data.datetime = self.data.datetime.dt.to_pydatetime() + time_jitter

        idx = (self.data.pickup_datetime >= from_datetime) & (self.data.pickup_datetime < to_datetime)
        self.data = self.data[idx]

        logging.debug(f"Time filtered number of trips: {self.data.shape[0]}")

        # if geofence:
        #     self.data = geo_filter(self.data, geofence)

        #     logging.debug(f"Geo filtered number of trips: {self.data.shape[0]}")

        if sample_size is not None:
            replace = self.data.index.shape[0] < sample_size
            index = state.choice(self.data.index, sample_size, replace=replace)
            self.data = self.data.loc[index]

        logging.debug(f"Sample size: {self.data.shape[0]}")

        self.data.pickup_datetime = self.data.pickup_datetime.dt.round(round_to)
        # self.data.datetime = self.data.datetime.dt.ceil(round_to)
        # self.data.datetime = self.data.datetime.dt.floor(round_to)

        self.demand = {g: item for g, item in self.data.groupby(self.data.pickup_datetime)}
        self.map_matcher = map_matcher

    def get_next(self, key):
        bookings = []
        seats = 1

        if key in self.demand:
            for b in self.demand[key].itertuples():
                pu = Position(b.pickup_lon, b.pickup_lat)
                do = Position(b.dropoff_lon, b.dropoff_lat)

                # TODO: if booking map matched too far from the original point????
                if self.map_matcher:
                    pu = self.map_matcher.map_match(pu)
                    do = self.map_matcher.map_match(do)

                id_ = uuid.UUID(int=self.rd.getrandbits(128)).hex
                bookings.append(Booking(self.clock, pu, do, seats, booking_id=id_))

        return bookings
