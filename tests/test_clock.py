import datetime
from math import ceil
from dateutil import parser
import pytest
from simobility.core.clock import Clock


@pytest.mark.parametrize(
    "time_unit,time_step,target_unit,target_time,expected",
    [
        ("h", 1, "h", 1, 1),
        ("h", 1, "m", 60, 1),
        ("h", 1, "m", 23, ceil(23 / 60)),
        ("m", 1, "h", 1, 60),
        ("m", 1, "h", 1, 60),
        ("m", 5, "h", 1, 12),
        ("m", 3, "m", 15, 5),
        ("m", 4, "m", 15, ceil(15 / 4)),
    ],
)
def test_time_to_clock_time(time_unit, time_step, target_unit, target_time, expected):
    assert (
        Clock(time_step=time_step, time_unit=time_unit).time_to_clock_time(
            target_time, target_unit
        )
        == expected
    )


@pytest.mark.parametrize(
    "time_unit,time_step,ticks,expected_hours,expected_minutes", [
        ('h', 0, 0, 0, 0),
        ('h', 1, 1, 1, 0),
        ('h', 3, 3, 9, 0),
        ('h', 1, 25, 1, 0),
        ('m', 10, 1, 0, 10),
        ('m', 10, 2, 0, 20),
        ('m', 10, 9, 1, 30)
        ]
)
def test_to_time_hour(time_unit, time_step, ticks, expected_hours, expected_minutes):
    clock = Clock(time_unit=time_unit, time_step=time_step)
    assert isinstance(clock.clock_time_to_time(), datetime.time)

    for _ in range(ticks):
        clock.tick()

    assert clock.clock_time_to_time().hour == expected_hours
    assert clock.clock_time_to_time().minute == expected_minutes


@pytest.mark.parametrize(
    "time_unit,time_step", [("m", 1), ("h", 1), ("m", 3), ("s", 50)]
)
def test_timeunits(time_unit, time_step):
    with pytest.raises(Exception):
        Clock(10, "sdsd")

    clock = Clock(time_step=time_step, time_unit=time_unit)
    assert clock.time_unit == time_unit
    assert clock.time_step == time_step
    assert clock.clock_time_to_time().minute == 0
    assert clock.clock_time_to_time().second == 1

@pytest.mark.parametrize(
    "time_unit,time_step,seconds,expected",
    [
        ("m", 1, 60, 60 * 60),
        ("m", 1, 65, 65 * 60),
        ("h", 1, 1, 60 * 60),
        ("s", 15, 1, 15),
        ("s", 45, 45, 45 * 45),
    ],
)
def test_time_to_seconds(time_unit, time_step, seconds, expected):
    clock = Clock(time_unit=time_unit, time_step=time_step)
    assert clock.clock_time_to_seconds(seconds) == expected


def test_to_time():
    starting_time = parser.parse("2016-06-02 07:55")
    clock = Clock(starting_time=starting_time, initial_time=23 * 60)

    assert clock.clock_time_to_time().hour == 6
    assert clock.clock_time_to_time().minute == 55


def test_to_time_starting_time():
    starting_time = parser.parse("2017-02-13 10:34")

    clock = Clock(time_step=10, time_unit="m", starting_time=starting_time)
    clock.tick()

    assert clock.clock_time_to_time().hour == 10
    assert clock.clock_time_to_time().minute == 44

    for i in range(3):
        clock.tick()

    assert clock.clock_time_to_time().hour == 11
    assert clock.clock_time_to_time().minute == 14


def test_to_time_starting_time_2():
    starting_time = parser.parse("2017-02-13 23:56")

    clock = Clock(time_step=10, time_unit="m", starting_time=starting_time)
    clock.tick()

    assert clock.clock_time_to_time().hour == 0
    assert clock.clock_time_to_time().minute == 6


def test_to_datetime():
    starting_time = parser.parse("2016-03-21 08:03")

    clock = Clock(time_step=1, time_unit="h", starting_time=starting_time)
    clock.tick()

    assert isinstance(clock.to_datetime(), datetime.datetime)
    assert clock.to_datetime() == parser.parse("2016-03-21 09:03")

    for i in range(25):
        clock.tick()

    assert clock.to_datetime() == parser.parse("2016-03-22 10:03")


def test_to_datetime2():
    starting_time = parser.parse("2016-06-02 16:25")

    clock = Clock(starting_time=starting_time, initial_time=60 * 12)

    assert clock.to_datetime() == parser.parse("2016-06-03 04:25")


def test_seconds_conversion():
    clock = Clock(time_step=43, time_unit="s")
    pytest.approx(clock.time_to_clock_time(67, "s")) == ceil(67 / 43)
