from abc import ABC, abstractmethod
from typing import List
from ..core.position import BasePosition
from .route import BaseRoute


class BaseRouter(ABC):

    @abstractmethod
    def map_match(self, position: BasePosition) -> BasePosition:
        return NotImplemented

    @abstractmethod
    def calculate_route(self, origin: BasePosition, destination: BasePosition) -> BaseRoute:
        """Calculate route between 2 points"""

        return NotImplemented

    @abstractmethod
    def estimate_duration(self, origin: BasePosition, destination: BasePosition) -> int:
        """Duration in clock units"""

        return NotImplemented

    @abstractmethod
    def calculate_distance_matrix(
        self,
        sources: List[BasePosition],
        destinations: List[BasePosition],
        travel_time: bool = True,
    ) -> List[List[float]]:
        """Calculate all-to-all travel time - all source to all destinations.
        Here distance means "distance in time"

        Parameters
        ----------

        sources: List[BasePosition]
        destinatiobs: List[BasePosition]

        Returns
        -------
        
        All-to-all trip durations (distance in time) in clock units (``distance_matrix``)
        
        """
        return NotImplemented
