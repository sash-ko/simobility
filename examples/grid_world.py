from typing import Tuple, Dict, List
import numpy as np
from scipy.spatial.distance import cityblock
from simobility.routers.base_router import BaseRouter
from simobility.core import BasePosition
from simobility.routers import BaseRoute


class Cell(BasePosition):

    def __init__(self, x, y):
        super().__init__()

        self.x = x
        self.y = y

    def distance(self, pos: 'Cell') -> int:
        return cityblock(self.coods, pos.coords)

    @property
    def coords(self) -> Tuple:
        return (self.x, self.y)

    def __eq__(self, other) -> bool:
        return self.id == other.id or self.coords == other.coords

    def to_dict(self) -> Dict:
        return {
            'x': self.x,
            'y': self.y
        }


class CellRoute(BaseRoute):

    def __init__(
        self,
        created_at: int,
        coordinates: List[Cell],
        duration: int,
        distance: float,
        origin: Cell,
        destination: Cell,
    ):
        super().__init__(created_at, coordinates, duration, distance, origin, destination)

    def approximate_position(self, at_time: int) -> Cell:
        if at_time > len(self.coordinates):
            return self.destination

        return self.coordinates[at_time]

    def traveled_distance(self, at_time: int) -> float:
        pos = self.approximate_position(at_time)
        return pos.distance(self.origin)


class CityBlockRouter(BaseRouter):

    def __init__(self, clock):
        super().__init__()
        self.clock = clock

    def map_match(self, cell: Cell) -> Cell:
        return cell

    def calculate_route(self, origin: Cell, destination: Cell) -> CellRoute:
        path = find_path(origin.coords, destination.coords)
        path = [Cell(*cell) for cell in path]
        # speed=1 so distance and duration are equal
        distance = origin.distance(destination)

        route = CellRoute(self.clock.now, path, distance, distance, origin, destination)
        return route
    
    def estimate_duration(self, origin: Cell, destination: Cell) -> int:
        # speed = 1
        return origin.distance(destination)

    def calculate_distance_matrix(
        self,
        sources: List[Cell],
        destinations: List[Cell],
        travel_time: bool = True,
    ) -> List[List[float]]:

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


def find_path(from_cell, to_cell, dimentions=2):
    grads = []
    for dim in range(dimentions):
        dv = gradient(to_cell[dim], from_cell[dim])
        grads.append(dv)

    path = [from_cell[:]]
    while from_cell != to_cell:
        for dim in range(dimentions):
            if grads[dim] and from_cell[dim] != to_cell[dim]:
                from_cell[dim] += grads[dim]
                path.append(from_cell[:])

    return path


def gradient(x1, x2):
    if x1 == x2:
        return 0
    dx = x1 - x2
    return int(dx / abs(dx))


class GridWorldDispatcher:
    def step(self):
        pass


def random_cell(width: int, height: int) -> Cell:
    pass


if __name__ == "__main__":
    print(find_path([5, 5], [12, 3]))
