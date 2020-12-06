from typing import Tuple, Dict, List
import numpy as np
from functools import partial
import random
from scipy.spatial.distance import cityblock
from simobility.routers.base_router import BaseRouter
from simobility.core import BasePosition
from simobility.routers import BaseRoute
from simobility.core import Dispatcher
from simobility.core import loggers
from simobility.core import Clock
from simobility.core import Fleet
from simobility.core import Vehicle
from simobility.core import Booking
from simobility.simulator.simulator import Simulator, Context
from simobility.core import BookingService
from greedy_matcher import GreedyMatcher


class Cell(BasePosition):
    def __init__(self, x, y):
        super().__init__()

        self.x = x
        self.y = y

    def distance(self, pos: "Cell") -> int:
        return cityblock(self.coords, pos.coords)

    @property
    def coords(self) -> Tuple:
        return (self.x, self.y)

    def __eq__(self, other) -> bool:
        return self.id == other.id or self.coords == other.coords

    def to_dict(self) -> Dict:
        return {"x": self.x, "y": self.y}


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
        super().__init__(
            created_at, coordinates, duration, distance, origin, destination
        )

    def approximate_position(self, at_time: int) -> Cell:
        if at_time >= len(self.coordinates):
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


def find_path(
    from_cell: List[int], to_cell: List[int]
) -> List[List[int]]:
    dimentions = 2
    from_cell = list(from_cell)
    to_cell = list(to_cell)

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


def gradient(x1: int, x2: int) -> int:
    """Calculate value and direction of change of x1 to
    get closer to x2. It can be one: -1, 0, 1
    """

    if x1 == x2:
        return 0

    dx = x1 - x2
    return int(dx / abs(dx))


def random_cell(width: int, height: int) -> List[int]:
    return [random.randint(0, width), random.randint(0, height)]


def create_fleet(num_vehicles, clock, cell_fn) -> Fleet:
    router = CityBlockRouter(clock)
    fleet = Fleet(clock, router)

    for i in range(num_vehicles):
        vehicle = Vehicle(clock)
        fleet.infleet(vehicle, Cell(*cell_fn()))

    return fleet


class RandomRequests:
    def __init__(self, clock, cell_fn):
        super().__init__()
        self.clock = clock
        self.cell_fn = cell_fn

    def next(self) -> List[Booking]:
        origin = self.cell_fn()
        destination = self.cell_fn()
        if origin == destination:
            return []

        return [Booking(self.clock, Cell(*origin), Cell(*destination))]


if __name__ == "__main__":
    loggers.configure_root_logger()

    # create in-memory log handler to be able to access to all
    # state changes after the simulation is over
    simulation_logs = loggers.InMemoryLogHandler()
    _ = loggers.get_simobility_logger(simulation_logs)

    clock = Clock(
        time_step=30, time_unit="s", starting_time="2020-11-11 13:00:01", initial_time=1
    )
    print(f"Current time {clock.to_datetime()} ({clock.now} clock time)")

    world_width = 10
    world_height = 10
    num_vehicles = 2
    max_pending_time = 5

    random_cell_fn = partial(random_cell, world_width, world_height)

    dispatcher = Dispatcher()
    booking_service = BookingService(clock, max_pending_time)

    fleet = create_fleet(num_vehicles, clock, random_cell_fn)

    context = Context(
        clock=clock, fleet=fleet, booking_service=booking_service, dispatcher=dispatcher
    )
    matcher = GreedyMatcher(
        context, fleet.router, search_radius=max(world_width, world_height)
    )

    simulator = Simulator(matcher, context)

    requests = RandomRequests(clock, random_cell_fn)
    simulator.simulate(requests, 10)

    print("\nSimulation state changes log:")
    print(simulation_logs.logs)
