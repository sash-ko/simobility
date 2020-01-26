import pytest
from unittest.mock import MagicMock
from simobility.core.vehicle_engine import VehicleEngine
from simobility.core.vehicle import Vehicle, States, StopReasons
from simobility.core import Clock, Position
from simobility.routers import LinearRouter


def test_create_vehicle():
    v = Vehicle(Clock())

    assert v.state == States.offline
    assert v.position is None
    assert v.destination is None

    # TODO: check particular type of exception
    with pytest.raises(Exception):
        v.stop()

    with pytest.raises(Exception):
        v.move_to(111)

    with pytest.raises(Exception):
        v.step()

    engine = MagicMock()
    engine.route = MagicMock()
    engine.route.duration = 23
    engine.route.distance = 2.34
    engine.route.traveled_distance = MagicMock(return_value=43)

    engine.position = MagicMock()
    engine.position.to_dict = MagicMock(return_value={111: 22})
    
    v.install_engine(engine)
    assert v.state == States.idling

    with pytest.raises(Exception):
        v.install_engine(engine)


def test_dont_move_vehicle():
    init_pos = Position(13.3764, 52.5461)
    dest1 = Position(13.4014, 52.5478)

    clock = Clock()
    router = LinearRouter(clock)

    engine = VehicleEngine(init_pos, router, clock)

    v = Vehicle(clock)
    v.install_engine(engine)

    assert v.position == init_pos
    assert v.destination is None

    v.move_to(init_pos)
    assert not v.engine.is_moving()
    assert v.engine.current_position == init_pos
    assert v.state == States.idling

    assert v.position == init_pos

    v.step()
    assert v.state == States.idling
    assert not v.engine.is_moving()
    assert v.engine.destination is None

    assert v.position == init_pos

    assert v.state == States.idling
    assert not v.engine.is_moving()
    assert v.engine.current_position == init_pos
    assert not v.is_moving

def test_move_vehicle():
    init_pos = Position(13.3764, 52.5461)
    dest1 = Position(13.4014, 52.5478)

    clock = Clock()
    router = LinearRouter(clock)

    engine = VehicleEngine(init_pos, router, clock)

    v = Vehicle(clock)
    v.install_engine(engine)

    context = {}
    v.move_to(dest1, context)
    assert v.engine.is_moving()
    assert v.state == States.moving_to

    v.step()
    assert v.state == States.moving_to
    assert v.engine.is_moving()

    clock.tick()
    v.step()

    assert v.engine.is_moving()

    for _ in range(1000):
        clock.tick()
        v.step()

        if not v.engine.is_moving():
            assert v.position == dest1
            assert v.state == States.idling
        else:
            assert v.position != dest1
            assert v.destination == dest1
            assert v.state == States.moving_to
