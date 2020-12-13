from abc import ABC, abstractmethod
from typing import List
from math import ceil
from ..core.base_position import BasePosition


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

        created_at: int
            Time when the route was created

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
        """It is assumed that a vehicle starts moving right after a route
        was created so the traveled time is a difference between curren time
        and the time when the route was created"""
        return at_time - self.created_at

    @abstractmethod
    def approximate_position(self, at_time: int) -> BasePosition:
        """Get an approximated position of a vehicle at any point of time"""
        pass

    @abstractmethod
    def traveled_distance(self, at_time: int) -> float:
        """Distance traveled from the original position to an approximate
        position of a cetrain point of time"""
        pass
