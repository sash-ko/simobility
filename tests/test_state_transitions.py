import pytest
from unittest.mock import patch
from unittest.mock import MagicMock
from simobility.core import Vehicle, Booking, Itinerary
from simobility.core.vehicle_engine import VehicleEngine
from simobility.core import Clock, Position
from simobility.routers import LinearRouter
from simobility.core.state_transitions import *


def create_itinenary():
    itinerary = MagicMock()
    itinerary.current_job = MagicMock()
    itinerary.current_job.eta = 11
    itinerary.current_job.destinaton = "destination"
    # no next jobs
    itinerary.next_jobs = []
    return itinerary


def create_vehicle():
    vehicle = MagicMock()
    vehicle.is_moving = MagicMock(return_value=True)
    vehicle.move_to = MagicMock()
    vehicle.destination = "go there"
    return vehicle


def create_pickup_dropoff(is_pickup):
    job = MagicMock()
    job.is_pickup = MagicMock(return_value=is_pickup)
    job.is_dropoff = MagicMock(return_value=not is_pickup)

    job.booking.id = 3434
    return job


# ######################################################
# # Test vehicle_moving
# ######################################################


def test_move_vehicle_moving():
    """Test move_vehicle for Vehicle that is moving"""
    itinerary = create_itinenary()
    vehicle = create_vehicle()
    itinerary.vehicle = vehicle

    # job to move to the same location - nothing should happend
    vehicle.destination = itinerary.current_job.destination
    move_vehicle(itinerary)
    vehicle.move_to.assert_called()

    vehicle.move_to = MagicMock()

    # vehicle moving to a different location - move_to function
    # should be called with new destination
    vehicle.destination = "somewhere else"
    move_vehicle(itinerary)

    vehicle.move_to.assert_called_once_with(
        itinerary.current_job.destination, itinerary=itinerary
    )


def test_vehicle_not_moving():
    itinerary = create_itinenary()
    vehicle = create_vehicle()
    vehicle.is_moving = False
    itinerary.vehicle = vehicle

    # if vehicle is already at the destination location
    vehicle.position = itinerary.current_job.destination
    move_vehicle(itinerary)
    vehicle.move_to.assert_called()

    vehicle.move_to = MagicMock()
    vehicle.position = "somehwere else"
    move_vehicle(itinerary)

    vehicle.move_to.assert_called_once_with(
        itinerary.current_job.destination, itinerary=itinerary
    )


def test_move_vehicle_moving_pickup():
    vehicle = create_vehicle()
    itinerary = create_itinenary()
    itinerary.vehicle = vehicle

    # move to pickup
    pickup = create_pickup_dropoff(True)
    itinerary.next_jobs = [pickup]

    vehicle.destination = "destination"
    move_vehicle(itinerary)

    vehicle.move_to.assert_called_once_with(
        itinerary.current_job.destination, itinerary=itinerary
    )


def test_move_vehicle_moving2dropoff():
    itinerary = create_itinenary()

    vehicle = create_vehicle()
    vehicle.destination = itinerary.current_job.destination

    # move to pickup
    dropoff = create_pickup_dropoff(False)
    itinerary.next_jobs = [dropoff]

    vehicle.destination = "somewhere else"
    itinerary.vehicle = vehicle
    move_vehicle(itinerary)

    vehicle.move_to.assert_called_once_with(
        itinerary.current_job.destination, itinerary=itinerary
    )


def test_real_vehicle():
    init_pos = Position(13.3764, 52.5461)
    dest = Position(13.4014, 52.5478)

    clock = Clock()
    router = LinearRouter(clock)

    engine = VehicleEngine(init_pos, router, clock)

    v = Vehicle(clock)
    v.install_engine(engine)

    itinerary = Itinerary(111, v)
    itinerary.move_to(dest)

    assert not v.is_moving

    move_vehicle(itinerary)

    assert v.is_moving


# ######################################################
# # Test pickup_booking
# ######################################################


def test_pickup_booking():
    vehicle = create_vehicle()
    itinerary = Itinerary(Clock(), vehicle)

    booking = MagicMock()
    booking.is_pending = MagicMock(return_value=True)
    booking.is_matched = MagicMock(return_value=True)

    context = {"vehicle_id": vehicle.id}
    pickup_booking(booking, itinerary)

    booking.set_matched.assert_called_once_with(itinerary=itinerary)
    booking.set_waiting_pickup.assert_called_once_with(itinerary=itinerary)
    booking.set_pickup.assert_called_once_with(itinerary=itinerary)

    booking = MagicMock()
    booking.is_pending = MagicMock(return_value=False)
    booking.is_matched = MagicMock(return_value=True)
    pickup_booking(booking, itinerary)
    booking.set_waiting_pickup.assert_called_once_with(itinerary=itinerary)
    booking.set_pickup.assert_called_once_with(itinerary=itinerary)

    booking = MagicMock()
    booking.is_pending = MagicMock(return_value=False)
    booking.is_matched = MagicMock(return_value=False)
    booking.is_waiting_pickup = MagicMock(return_value=True)
    pickup_booking(booking, itinerary)
    booking.set_pickup.assert_called_once_with(itinerary=itinerary)

    booking = MagicMock()
    booking.is_pending = MagicMock(return_value=False)
    booking.is_matched = MagicMock(return_value=False)
    booking.is_waiting_pickup = MagicMock(return_value=False)

    with pytest.raises(NotImplementedError):
        pickup_booking(booking, itinerary)


# ######################################################
# # Test dropoff_booking
# ######################################################


def test_dropoff_booking():
    vehicle = create_vehicle()
    itinerary = Itinerary(Clock(), vehicle)

    booking = MagicMock()
    booking.is_waiting_dropoff = MagicMock(return_value=True)
    dropoff_booking(booking, itinerary)
    booking.set_dropoff.assert_called_once_with(itinerary=itinerary)
    booking.set_complete.assert_called_once_with(itinerary=itinerary)

    booking = MagicMock()
    booking.is_waiting_dropoff = MagicMock(return_value=False)
    booking.is_pickup = MagicMock(return_value=True)
    dropoff_booking(booking, itinerary)
    booking.set_waiting_dropoff.assert_called_once_with(itinerary=itinerary)
    booking.set_dropoff.assert_called_once_with(itinerary=itinerary)
    booking.set_complete.assert_called_once_with(itinerary=itinerary)

    booking = MagicMock()
    booking.is_waiting_dropoff = MagicMock(return_value=False)
    booking.is_pickup = MagicMock(return_value=False)

    with pytest.raises(Exception):
        dropoff_booking(booking, itinerary)


# ######################################################
# # Test do_current_job
# ######################################################


def test_do_job():
    vehicle = MagicMock()
    itinerary = Itinerary(Clock(), vehicle)

    booking = MagicMock()
    booking.is_pending = MagicMock(return_value=False)
    booking.is_matched = MagicMock(return_value=True)

    job = MagicMock()
    job.is_pickup = MagicMock(return_value=True)
    job.is_dropoff = MagicMock(return_value=False)
    job.is_move_to = MagicMock(return_value=False)
    job.booking = booking

    itinerary.current_job = job

    do_job(itinerary)

    booking.set_waiting_pickup.assert_called_once_with(itinerary=itinerary)
    vehicle.move_to.assert_not_called()

    job.is_pickup = MagicMock(return_value=False)
    job.is_dropoff = MagicMock(return_value=True)
    itinerary.current_job = job

    booking.is_waiting_dropoff = MagicMock(return_value=True)
    do_job(itinerary)
    booking.set_dropoff.assert_called_once_with(itinerary=itinerary)
    vehicle.move_to.assert_not_called()

    job.is_pickup = MagicMock(return_value=False)
    job.is_dropoff = MagicMock(return_value=False)
    job.is_move_to = MagicMock(return_value=True)
    job.destination = "aaa"

    vehicle.is_moving = False
    vehicle.position = "bb"
    itinerary.current_job = job

    do_job(itinerary)

    vehicle.move_to.assert_called_once_with(job.destination, itinerary=itinerary)


def test_do_current_job_2():
    init_pos = Position(13.3764, 52.5461)
    dest = Position(13.4014, 52.5478)

    clock = Clock()
    router = LinearRouter(clock)

    engine = VehicleEngine(init_pos, router, clock)

    v = Vehicle(clock)
    v.install_engine(engine)

    itinerary = Itinerary(2, v)
    itinerary.move_to(dest)
    do_job(itinerary)

    assert v.is_moving


def test_do_current_job_3():
    v = create_vehicle()

    itinerary = Itinerary(12, v)
    job = itinerary.move_to(2323)

    with patch("simobility.core.state_transitions.move_vehicle") as fn:
        do_job(itinerary)
        fn.assert_called_once_with(itinerary)

    booking = 34
    itinerary = Itinerary(23, v)
    itinerary.pickup(booking)

    with patch("simobility.core.state_transitions.pickup_booking") as fn:
        do_job(itinerary)
        fn.assert_called_once_with(booking, itinerary)

    itinerary = Itinerary(4545, v)
    itinerary.dropoff(booking)

    with patch("simobility.core.state_transitions.dropoff_booking") as fn:
        do_job(itinerary)
        fn.assert_called_once_with(booking, itinerary)


# ######################################################
# # Test update_next_bookings
# ######################################################


def test_update_next_bookings():
    v = create_vehicle()

    clock = Clock()
    b1 = Booking(clock, Position(13.4014, 52.5478), Position(13.3393, 52.5053))
    b2 = Booking(clock, Position(13.4014, 52.5478), Position(13.3393, 52.5053))

    itinerary = Itinerary(3434, v)
    itinerary.move_to(111)
    itinerary.pickup(b1)
    itinerary.dropoff(b1)
    itinerary.pickup(b2)
    itinerary.dropoff(b2)

    update_next_bookings(itinerary)

    assert b1.is_waiting_pickup()
    assert b2.is_waiting_pickup()

    b1.set_pickup()
    update_next_bookings(itinerary)
    assert b1.is_waiting_dropoff()
    assert b2.is_waiting_pickup()
