import numpy as np
from abc import ABC, abstractmethod
from typing import List
from ..core.base_position import BasePosition
from .route import BaseRoute


class BaseRouter(ABC):

    @abstractmethod
    def map_match(self, position: BasePosition) -> BasePosition:
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
