from typing import List, Type, Dict
from .vehicle_engine import VehicleEngine
from .vehicle import StopReasons, Vehicle
from .clock import Clock
from .position import Position
from ..routers.base_router import BaseRouter


class Fleet:
    def __init__(self, clock: Clock, router: Type[BaseRouter]):
        # vehicle_id -> Vehicle
        self._vehicles: Dict[str, Vehicle] = {}
        self._router = router
        self.clock = clock

    def get_online_vehicles(self) -> List[Vehicle]:
        return [v for v in self._vehicles.values() if not v.is_offline()]

    def infleet(self, vehicle: Vehicle, position: Position):
        engine = create_engine(position, self._router, self.clock)
        vehicle.install_engine(engine)

        self._vehicles[vehicle.id] = vehicle

    def get_vehicle(self, vehicle_id: str) -> Vehicle:
        return self._vehicles[vehicle_id]

    def step(self):
        for v in self._vehicles.values():
            v.step()

    def stop_vehicles(self):
        for v in self._vehicles.values():
            if not v.is_idling():
                v.stop(StopReasons.stop)


def create_engine(pos: Position, router: Type[BaseRouter], clock: Clock):
    return VehicleEngine(pos, router, clock)
