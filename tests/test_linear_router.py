import pytest
from simobility.routers import LinearRouter
from simobility.core import Position
from simobility.core.clock import Clock


def test_router2d():
    speed_kmph = 25
    nyc_pos = Position(-73.935242, 40.730610)
    nyc_pos_shift = Position(-73.935, 40.7306)

    # monutes
    clock = Clock(time_step=1, time_unit="m")
    router = LinearRouter(speed=speed_kmph, clock=clock)

    assert (router.estimate_duration(nyc_pos, nyc_pos) == 0)

    route = router.calculate_route(nyc_pos, nyc_pos)
    assert (route.duration == 0)
    assert (route.distance == 0)
    assert (len(route.coordinates) == 1)

    assert (route.approximate_position(clock.clock_time) == nyc_pos)
    assert (route.approximate_position(clock.clock_time + 1) == nyc_pos)

    assert (router.estimate_duration(nyc_pos, nyc_pos_shift) == 1)

    for i in range(10):
        clock.tick()

    assert (router.estimate_duration(nyc_pos, nyc_pos) == 0)

    # seconds
    clock = Clock(time_step=1, time_unit="s")
    router = LinearRouter(speed=speed_kmph, clock=clock)
    assert (router.estimate_duration(nyc_pos, nyc_pos_shift) == 3)

    route = router.calculate_route(nyc_pos, nyc_pos_shift)
    assert route.duration == 3
    assert (pytest.approx(route.distance, 3) == 0.02)
    assert len(route.coordinates) == 4

    assert route.approximate_position(clock.clock_time) == nyc_pos
    assert route.approximate_position(clock.clock_time + 1) != nyc_pos
    assert (route.approximate_position(clock.clock_time + 1) == route.coordinates[1])

    assert (route.approximate_position(clock.clock_time + 3) == nyc_pos_shift)
    assert (
        route.approximate_position(clock.clock_time + 3) == route.coordinates[-1]
    )


def test_router2d_2():
    speed_kmph = 17

    nyc_pos = Position(-73.935242, 40.730610)
    nyc_pos_shift = Position(-73.935, 40.730610)

    clock = Clock(time_step=1, time_unit="s")
    router = LinearRouter(speed=speed_kmph, clock=clock)

    assert (router.estimate_duration(nyc_pos, nyc_pos_shift) == 5)

    route = router.calculate_route(nyc_pos, nyc_pos_shift)
    assert (len(route.coordinates) == 6)

    for p in route.coordinates:
        assert (p.lat == nyc_pos.lat)


def test_map_match():
    clock = Clock(time_step=1, time_unit="m")
    router = LinearRouter(speed=12, clock=clock)

    pos1 = Position(-0.39376, 39.5145)
    pos2 = Position(-0.38874, 39.503)

    for pos in [pos1, pos2]:
        pos_m = router.map_match(pos)
        assert pos == pos_m
        assert pos.id != pos_m.id

