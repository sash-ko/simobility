import pytest
from unittest.mock import MagicMock
from simobility.core.vehicle_engine import VehicleEngine
from simobility.core import Clock, Position, Booking, Vehicle
from simobility.routers import LinearRouter
from simobility.core import Itinerary, Fleet
from simobility.core import Dispatcher


def test_Dispatcher():
    clock = Clock()
    router = LinearRouter(clock)

    fleet = Fleet(clock, router)
    vehicle = Vehicle(clock)
    fleet.infleet(vehicle, Position(13.3764, 52.5461))

    cnt = Dispatcher()

    cnt.step()

    booking = Booking(clock, Position(13.4014, 52.5478), Position(13.3764, 52.5461))

    itinerary = Itinerary(101, vehicle)
    itinerary.move_to(Position(13.4014, 52.5478))
    itinerary.pickup(booking)
    itinerary.dropoff(booking)

    cnt.dispatch(itinerary)
    cnt.step()

    assert vehicle.is_moving
    assert booking.is_waiting_pickup()

    booking.set_pickup()

    cnt.dispatch(itinerary)
    cnt.step()

    assert booking.is_waiting_dropoff()


def test_Dispatcher_2():
    clock = Clock()
    router = LinearRouter(clock)

    fleet = Fleet(clock, router)
    vehicle = Vehicle(clock)
    fleet.infleet(vehicle, Position(13.3764, 52.5461))

    cnt = Dispatcher()

    booking = Booking(clock, Position(13.4014, 52.5478), Position(13.3764, 52.5461))

    itinerary = Itinerary(101, vehicle)
    job1 = itinerary.pickup(booking)
    job2 = itinerary.dropoff(booking)

    cnt.dispatch(itinerary)
    cnt.step()

    # finish 2 jobs in 1 step
    assert itinerary.current_job is None

    assert booking.is_complete()


def test_Dispatcher_3():
    clock = Clock()
    router = LinearRouter(clock)

    fleet = Fleet(clock, router)
    vehicle = Vehicle(clock)
    fleet.infleet(vehicle, Position(13.3764, 52.5461))

    cnt = Dispatcher()

    booking = Booking(clock, Position(13.4014, 52.5478), Position(13.3764, 52.5461))

    itinerary = Itinerary(101, vehicle)
    job1 = itinerary.pickup(booking)
    job2 = itinerary.move_to(Position(13.4014, 52.5478))
    job3 = itinerary.dropoff(booking)

    cnt.dispatch(itinerary)
    cnt.step()

    # finish 2 jobs in 1 step
    assert itinerary.current_job is job2

    assert booking.is_waiting_dropoff()
