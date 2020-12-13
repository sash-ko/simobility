import numpy as np
from abc import ABC, abstractmethod
from typing import List
from ..core.base_position import BasePosition
from .route import BaseRoute


class BaseRouter(ABC):
    """Router define how vehicles move. There are several advantages of using routers:

    - routers can define how vehocles move in different coordinates systems, for example,
        latitude and longitues, grid cells, e.g. And it does not require any additional
        changes a simulation - just replace a router and vehicles can move in a different way

    - routers help to avoind unnecessary and expencive recalculation of vehicle positions on
        each step of a simulation. They implement a "lazy" calculations - based on
        a coordinate system, origin and destination they calculate an approximate position
        an arrival time on demand. So a vehicle movement can be scheduled in advance:
        a vehicle V1 will arrive at point A in 20 minutes and currently this vehicle is
        at position B.

    - traffic

    """

    @abstractmethod
    def map_match(self, position: BasePosition) -> BasePosition:
        """Correct positiona according to a corrdinate system. For example, position
        can be a noisy GPS coordinate and it needs to be corrected by map matching
        to a road network"""
        pass

    @abstractmethod
    def calculate_route(self, origin: BasePosition, destination: BasePosition) -> BaseRoute:
        """Calculate route between 2 points"""
        pass

    @abstractmethod
    def estimate_duration(self, origin: BasePosition, destination: BasePosition) -> int:
        """Duration in clock units"""
        pass

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

        n_sources = len(sources)
        n_dest = len(destinations)

        matrix = np.zeros([n_sources, n_dest])

        for ind1, src in enumerate(sources):
            for ind2, dest in enumerate(destinations):

                if travel_time:
                    matrix[ind1, ind2] = self.estimate_duration(src, dest)
                else:
                    matrix[ind1, ind2] = src.distance(dest)

        return matrix
