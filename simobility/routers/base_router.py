from abc import ABCMeta, abstractmethod
from typing import List
from ..core.position import Position
from .route import Route


class BaseRouter(metaclass=ABCMeta):
    @abstractmethod
    def map_match(self, position: Position) -> Position:
        return NotImplemented

    @abstractmethod
    def calculate_route(self, origin: Position, destination: Position) -> Route:
        """Calculate route between 2 points

        :param origin: Position
        :param destination: Position
        :return: Route
        :rtype: Route
        """
        return NotImplemented

    @abstractmethod
    def estimate_duration(self, origin: Position, destination: Position) -> int:
        """Duration in clock units

        :param origin: Position
        :param destination: Position
        :return: Trip duration in clock units
        :rtype: int
        """
        return NotImplemented

    @abstractmethod
    def calculate_distance_matrix(
        self,
        sources: List[Position],
        destinations: List[Position],
        travel_time: bool = True,
    ) -> List[List[float]]:
        """Calculate all-to-all travel time - all source to all destinations.
        Here distance means "distance in time"

        :param sources: List of Positions
        :param destinations: List of Positions
        :return: All-to-all trip durations (distance in time) in clock units (``distance_matrix``)
        :rtype: np.array
        """
        return NotImplemented
