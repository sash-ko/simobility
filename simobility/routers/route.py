import logging
from math import ceil
from typing import List

from .utils import linear_approximation
from ..core.position import Position


class Route:
    """
    Contains information about a route - duration, distace, coordinates
    """

    def __init__(
        self,
        created_at: int,
        coordinates: List[Position],
        duration: int,
        distance: float,
        origin: Position,
        destination: Position,
    ):
        """
        Params
        ------

        coordinates : list
            List of points that represent the route

        duration : int
            Travel time between origin and destination of the route

        distance : float
            Route distance in kilometers

        origin: Position
        destination: Postion
            Requested origin and destination of a route. Due to
            map matching they can be different from the first and
            the last point in coordinates
        """

        self.coordinates = coordinates
        self.distance = distance
        # round to ensure that this is a clock time which is always integer
        self.duration = ceil(duration)
        self.created_at = created_at
        self.origin = origin
        self.destination = destination

        # internal variables
        segments = list(zip(self.coordinates, self.coordinates[1:]))
        seg_distance = [p1.distance(p2) for p1, p2 in segments]
        self.__segment_distance: List[float] = seg_distance

    @property
    def arrival_time(self):
        return self.created_at + self.duration

    def approximate_position(self, at_time: int) -> Position:
        """Approximate position on the route at specific time"""

        points = [p.coords for p in self.coordinates]

        pos = Position(*points[-1])

        if self.duration > 0:

            # calculate percentage of trip accomplished by the time
            pcnt = (at_time - self.created_at) / self.duration
            # if the method is called long after the trip was finished
            pcnt = min(1, pcnt)

            coords = linear_approximation(pcnt, points, self.__segment_distance)
            pos = Position(*coords)

        return pos

    def traveled_distance(self, at_time: int) -> float:
        duration = 0.0

        if self.duration > 0:
            pcnt = (at_time - self.created_at) / self.duration
            # if the method is called long after the trip was finished
            pcnt = min(1, pcnt)
            duration = self.distance * pcnt

        return duration

    def traveled_time(self, at_time: int) -> int:
        return at_time - self.created_at
