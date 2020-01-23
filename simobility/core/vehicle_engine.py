import logging
from typing import Type, Optional
from .position import Position
from .clock import Clock
from ..routers.route import Route
from ..routers.base_router import BaseRouter


class VehicleEngine:
    """ Moves vehicles. Every time `start_move` is called, VehicleEngine calculates
    a route and `is_moving` will be true until the end of the route.

    The route is the one that is used to move vehicles, the ground truth. It not necessary 
    the same as the one used by matcher/dispatcher. This route can be calculated
    from historical data or include real time traffic information.
    """

    def __init__(self, position: Position, router: Type[BaseRouter], clock: Clock):
        self.router = router
        self.clock = clock
        # The value of the position is valid only when
        # vehicle has arrived to the destination or was stopped
        # To get actuall position use _position_ property
        self._position = position

        # "Scheduled" time of arrival to the destination - every time move_to
        # method is called, it calculates the time of arrival to the destination
        # using router and it is used to detect when vehicle has arrived to the
        # destination
        self.route: Optional[Route] = None

    def start_move(self, destination: Position):
        """Sent engine to a specific destination or change the current destination
        of the current move"""

        if self._position is None:
            raise Exception("Cannot move engine with unknown current position")

        if not self.route:
            route = self.router.calculate_route(self.current_position, destination)
            if route.duration > 0:
                self.route = route
        else:
            raise Exception("Engine is already moving")

    def end_move(self):
        """Reset route, set position to the position estimated by router and
        set time of arrival to None"""

        if self.route:
            if not self.is_moving():
                self._position = self.route.destination
            else:
                self._position = self.route.approximate_position(self.now)
        self.route = None

    @property
    def destination(self) -> Optional[Position]:
        if self.route:
            return self.route.destination
        return None

    @property
    def eta(self) -> int:
        """Time of arrival"""
        if self.route:
            return self.route.arrival_time
        return self.now

    def is_moving(self) -> bool:
        return self.eta > self.now

    @property
    def current_position(self) -> Optional[Position]:
        """Current position of the engine. If engine is moving position
        will be approximated knowing current route and time
        """
        if self.route and self._position != self.route.destination:
            return self.route.approximate_position(self.now)
        else:
            return self._position

    @property
    def now(self) -> int:
        return self.clock.clock_time
