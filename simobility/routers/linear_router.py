import numpy as np
from math import ceil
from typing import List, Tuple

from ..core.position import Position
from .route import Route
from .base_router import BaseRouter


class LinearRouter(BaseRouter):
    """ Calculates routes as straight lines and haversine distances,
    kind of "bee line" distance

    Usage sample::

        >>> from simobility.routers.linear_router import LinearRouter
        >>> my_router = LinearRouter(clock=clock, speed=speed_kmph)
    """

    def __init__(self, clock, speed: int = 20):
        self.clock = clock
        self.speed = speed

    def map_match(self, position: Position) -> Position:
        return Position(*position.coords)

    def calculate_route(self, origin: Position, destination: Position) -> Route:
        """
        Calculate route between 2 points

        Params
        ------

        origin : Position
        destination : Position

        Returns
        -------

        route : Route
        """

        trip_duration = self.estimate_duration(origin, destination)

        y = np.linspace(origin.lat, destination.lat, trip_duration + 1)
        x = np.linspace(origin.lon, destination.lon, trip_duration + 1)

        path = np.array([x, y]).T.tolist()
        waypoints = [Position(x_, y_) for x_, y_ in path]

        distance_km = origin.distance(destination)

        return Route(
            self.clock.now, waypoints, trip_duration, distance_km, origin, destination
        )

    def estimate_duration(self, origin: Position, destination: Position) -> int:
        """ Duration in clock units

        Params
        ------

        origin : Position
        destination : Position

        Returns
        -------

        duration : int
            Trip duration in clock units
        """

        distance_km = origin.distance(destination)
        # convert to minutes
        travel_time = distance_km / self.speed * 60

        return ceil(self.clock.time_to_clock_time(travel_time, "m"))
