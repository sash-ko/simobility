from unittest.mock import MagicMock
from simobility.core.vehicle_engine import VehicleEngine
from simobility.core import Position
from simobility.core.clock import Clock
from simobility.routers import LinearRouter


def create_route_mock(dest, duration):
    route = MagicMock()
    route.destination = dest
    route.duration = duration
    return route


def test_create():
    router = MagicMock()
    position = MagicMock()
    clock = MagicMock()
    clock.clock_time = 2

    v = VehicleEngine(position, router, clock)

    assert not v.is_moving()
    assert v.current_position == position
    assert v.eta == clock.clock_time


def test_now():
    clock = MagicMock()
    clock.clock_time = 324

    v = VehicleEngine(MagicMock(), MagicMock(), clock)

    assert v.now == clock.clock_time
    clock.clock_time += 1
    assert v.now == clock.clock_time


def test_move_to_same():
    """Move to the same position is current pos of the vehicle"""
    router = MagicMock()
    position = MagicMock()
    clock = MagicMock()
    clock.clock_time = 10

    v = VehicleEngine(position, router, clock)

    route = create_route_mock(position, 0)
    router.calculate_route = MagicMock(return_value=route)

    v.start_move(position)

    assert v.eta == clock.clock_time
    assert not v.is_moving()
    assert v.current_position == position
    
    # don't rise an exception
    v.start_move(position)


def test_move_to():
    router = MagicMock()
    position = MagicMock()
    position2 = MagicMock()

    clock = MagicMock()
    clock.clock_time = 25

    v = VehicleEngine(position, router, clock)

    route = create_route_mock(position2, 4)
    router.calculate_route = MagicMock(return_value=route)

    v.start_move(position2)

    route.arrival_time = clock.clock_time + route.duration
    assert v.eta == clock.clock_time + route.duration
    assert v.is_moving()
    
    assert v.current_position != position2
    
    # one time step before arrival
    clock.clock_time = clock.clock_time + route.duration - 1
    assert v.is_moving()
    assert v.current_position != position2

    # arrival time
    clock.clock_time = clock.clock_time + 1
    assert not v.is_moving()


def test_stop_start():
    """Test stop at the beginning of trip"""
    router = MagicMock()
    position = MagicMock()
    position2 = MagicMock()

    clock = MagicMock()
    clock.clock_time = 11

    v = VehicleEngine(position, router, clock)
    v.end_move()

    assert v.current_position == position

    route = create_route_mock(position2, 3)
    route.arrival_time = clock.clock_time + route.duration
    router.calculate_route = MagicMock(return_value=route)
    route.approximate_position = MagicMock(return_value=position)
    v.start_move(position2)

    assert v.current_position == position
    assert v.current_position != position2
    assert v.is_moving()

    v.end_move()

    assert v.route is None
    assert not v.is_moving()
    assert v.eta == clock.clock_time
    # has not arrived yet
    assert v.current_position != position2
    assert v.current_position == position


def test_stop_end():

    router = MagicMock()
    position2 = MagicMock()

    clock = MagicMock()
    clock.clock_time = 11

    v = VehicleEngine(MagicMock(), router, clock)

    route = create_route_mock(position2, 4)
    router.calculate_route = MagicMock(return_value=route)
    route.arrival_time = clock.clock_time + route.duration
    v.start_move(position2)

    assert v.eta == clock.clock_time + route.duration

    clock.clock_time = clock.clock_time + route.duration
    v.end_move()

    assert v.route is None
    assert v.eta == clock.clock_time
    assert not v.is_moving()
    assert v.current_position == position2


def test_future_move():
    router = MagicMock()
    position2 = MagicMock()

    clock = MagicMock()
    clock.clock_time = 11

    v = VehicleEngine(MagicMock(), router, clock)

    route = create_route_mock(position2, 4)
    router.calculate_route = MagicMock(return_value=route)
    route.arrival_time = clock.clock_time + route.duration
    v.start_move(position2)

    clock.clock_time = clock.clock_time + route.duration + 1

    assert v.is_moving() is False


def test_end_to_end():

    init_pos = Position(13.3764, 52.5461)
    dest1 = Position(13.4014, 52.5478)
    dest2 = Position(13.3393, 52.5053)

    clock = Clock()
    # to start not from the beginning
    clock.tick()
    clock.tick()

    router = LinearRouter(clock)

    engine = VehicleEngine(init_pos, router, clock)
    engine.start_move(dest1)

    assert engine.eta == 8
    assert engine.current_position == init_pos

    clock.tick()
    clock.tick()

    assert engine.current_position != init_pos

    for _ in range(engine.eta - clock.clock_time):
        clock.tick()

    assert engine.current_position == dest1
    assert not engine.is_moving()
    assert engine.eta == clock.clock_time

    engine.end_move()
    assert not engine.is_moving()
    assert engine.eta == clock.clock_time
