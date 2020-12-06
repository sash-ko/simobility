from abc import ABC, abstractmethod
from typing import List
from math import ceil
from ..core.position import Position, BasePosition


class BaseRoute(ABC):
    """
    Contains information about a route - duration, distace, coordinates
    """

    def __init__(
        self,
        created_at: int,
        coordinates: List[BasePosition],
        duration: int,
        distance: float,
        origin: BasePosition,
        destination: BasePosition,
    ):
        """
        Parameters
        ----------

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

    @property
    def arrival_time(self) -> int:
        return self.created_at + self.duration

    def traveled_time(self, at_time: int) -> int:
        return at_time - self.created_at

    @abstractmethod
    def approximate_position(self, at_time: int) -> BasePosition:
        pass

    @abstractmethod
    def traveled_distance(self, at_time: int) -> float:
        pass
