from typing import List

from .utils import linear_approximation
from ..core.geo_position import GeographicPosition
from .base_route import BaseRoute


class Route(BaseRoute):
    def __init__(
        self,
        created_at: int,
        coordinates: List[GeographicPosition],
        duration: int,
        distance: float,
        origin: GeographicPosition,
        destination: GeographicPosition,
    ):

        super().__init__(
            created_at, coordinates, duration, distance, origin, destination
        )

        # internal variables
        segments = list(zip(self.coordinates, self.coordinates[1:]))
        seg_distance = [p1.distance(p2) for p1, p2 in segments]
        self.__segment_distance: List[float] = seg_distance

    def approximate_position(self, at_time: int) -> GeographicPosition:
        """Approximate position on the route at specific time"""

        points = [p.coords for p in self.coordinates]

        pos = GeographicPosition(*points[-1])

        if self.duration > 0:

            # calculate percentage of trip accomplished by the time
            pcnt = (at_time - self.created_at) / self.duration
            # if the method is called long after the trip was finished
            pcnt = min(1, pcnt)

            coords = linear_approximation(pcnt, points, self.__segment_distance)
            pos = GeographicPosition(*coords)

        return pos

    def traveled_distance(self, at_time: int) -> float:
        duration = 0.0

        if self.duration > 0:
            pcnt = (at_time - self.created_at) / self.duration
            # if the method is called long after the trip was finished
            pcnt = min(1, pcnt)
            duration = self.distance * pcnt

        return duration
