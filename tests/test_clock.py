import datetime
from math import ceil
from dateutil import parser
import pytest
from simobility.core.clock import Clock


def test_tick():
    clock = Clock()

    for i in range(10):
        assert clock.clock_time == i
        clock.tick()


def test_starting_time():
    clock = Clock()
    assert isinstance(clock.to_datetime(), datetime.datetime)
    assert clock.clock_time_to_time().hour == 0
    assert clock.clock_time_to_time().minute == 0
    assert clock.clock_time_to_time().second == 1


def test_timeunits():
    with pytest.raises(Exception):
        Clock(10, "sdsd")

    clock = Clock()
    assert clock.time_unit == "m"
    assert clock.time_step == 1

    clock = Clock(time_unit="h")
    assert clock.time_unit == "h"
    assert clock.time_step == 1

    clock = Clock(time_step=3, time_unit="m")
    assert clock.time_unit == "m"
    assert clock.time_step == 3


def test_time_to_clock_time():
    assert Clock(time_unit="h").time_to_clock_time(1, "h") == 1
    assert Clock(time_unit="h").time_to_clock_time(60, "m") == 1
    assert Clock(time_unit="h").time_to_clock_time(23, "m") == ceil(23 / 60)

    assert Clock(time_unit="m").time_to_clock_time(1, "h") == 60
    assert Clock(time_step=5, time_unit="m").time_to_clock_time(1, "h") == 12

    assert Clock(time_step=3, time_unit="m").time_to_clock_time(15, "m") == 5

    assert pytest.approx(
        Clock(time_step=4, time_unit="m").time_to_clock_time(15, "m")
    ) == ceil(15 / 4)


def test_to_time_hour():
    clock = Clock(time_unit="h")

    clock.tick()
    assert isinstance(clock.clock_time_to_time(), datetime.time)
    assert clock.clock_time_to_time().hour == 1
    assert clock.clock_time_to_time().minute == 0

    clock.tick()
    assert clock.clock_time_to_time().hour == 2
    assert clock.clock_time_to_time().minute == 0

    for i in range(24):
        clock.tick()

    assert clock.clock_time_to_time().hour == 2
    assert clock.clock_time_to_time().minute == 0

    for i in range(5):
        clock.tick()

    assert clock.clock_time_to_time().hour == 7


def test_to_time_hour_2():
    clock = Clock(time_step=2, time_unit="h")

    clock.tick()
    assert clock.clock_time_to_time().hour == 2
    assert clock.clock_time_to_time().minute == 0

    for i in range(24):
        clock.tick()

    assert clock.clock_time_to_time().hour == 2
    assert clock.clock_time_to_time().minute == 0


def test_to_time():
    starting_time = parser.parse("2016-06-02 07:55")
    clock = Clock(starting_time=starting_time, initial_time=23 * 60)

    assert clock.clock_time_to_time().hour == 6
    assert clock.clock_time_to_time().minute == 55


def test_to_time_minutes():
    clock = Clock(time_step=10, time_unit="m")
    clock.tick()

    assert clock.clock_time_to_time().hour == 0
    assert clock.clock_time_to_time().minute == 10

    clock.tick()
    assert clock.clock_time_to_time().hour == 0
    assert clock.clock_time_to_time().minute == 20

    for i in range(5):
        clock.tick()

    assert clock.clock_time_to_time().hour == 1
    assert clock.clock_time_to_time().minute == 10

    for i in range(24 * 60):
        clock.tick()

    assert clock.clock_time_to_time().hour == 1
    assert clock.clock_time_to_time().minute == 10


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


def test_time_to_seconds():
    clock = Clock(time_unit="m", time_step=1)
    assert clock.clock_time_to_seconds(60) == 60 * 60
    assert clock.clock_time_to_seconds(65) == 65 * 60

    clock = Clock(time_unit="h", time_step=1)
    assert clock.clock_time_to_seconds(1) == 60 * 60

    clock = Clock(time_unit="s", time_step=15)
    assert clock.clock_time_to_seconds(1) == 15

    clock = Clock(time_unit="s", time_step=45)
    assert clock.clock_time_to_seconds(45) == 45 * 45
