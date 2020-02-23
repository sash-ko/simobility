import numpy as np
from typing import List, Dict, Tuple
from collections import OrderedDict
from .base_router import BaseRouter
from ..core.position import Position
from .route import Route


class CachingRouter:

    # TODO: add cache expiration time
    def __init__(self, router: BaseRouter):
        self.__router = router
        self.__routes: Dict[Tuple, Route] = FixedSizeCache()
        self.__durations: Dict[Tuple, int] = FixedSizeCache()
        self.__map_match: Dict[Tuple, Position] = FixedSizeCache()
        self.clock = router.clock

    def map_match(self, position: Position) -> Position:
        key = position.coords
        if key in self.__map_match:
            return self.__map_match[key]

        pos = self.__router.map_match(position)
        self.__map_match[key] = pos
        return pos

    def calculate_route(self, origin: Position, destination: Position) -> Route:
        key = (origin.coords, destination.coords)
        route = self.__routes.get(key)
        if route is None:
            route = self.__router.calculate_route(origin, destination)
            self.__routes[key] = route
        route.created_at = self.clock.now
        return route

    def estimate_duration(self, origin: Position, destination: Position) -> int:
        key = (origin.coords, destination.coords)
        duration = self.__durations.get(key)

        if duration is None:
            duration = self.__router.estimate_duration(origin, destination)
            self.__durations[key] = duration

        return duration

    def calculate_distance_matrix(
        self, sources: List[Position], destinations: List[Position]
    ) -> np.array:

        sources = sources[:]
        destinations = destinations[:]

        updated_sources = []
        calculated = []
        missing = dict()

        for idx, s in enumerate(sources):
            distances = []

            for d in destinations:
                distances.append(self.__durations.get((s.coords, d.coords)))

            if not all(distances):
                missing[len(updated_sources)] = idx
                updated_sources.append(s)
                calculated.append([])
            else:
                calculated.append(distances)

        matrix = self.__router.calculate_distance_matrix(updated_sources, destinations)

        for k, v in missing.items():
            distances = matrix[k]
            calculated[v] = distances

            for idx, d in enumerate(destinations):
                s = sources[v]
                self.__durations[(s.coords, d.coords)] = distances[idx]

        matrix = np.array(calculated)

        return matrix


class FixedSizeCache(OrderedDict):
    """
    Dictionary that stores fixed number of items. Every time
    the size of the dictionary grows to maxsize, items removed in FIFO order
    """

    def __init__(self, maxsize=10240, *args, **kwargs):
        self.maxsize = maxsize
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if len(self) > self.maxsize:
            self.popitem(last=True)
