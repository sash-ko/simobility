import pytest
from unittest.mock import MagicMock
from simobility.core.booking import Booking, States
from simobility.core import Position, Clock


def test_create():
    pickup = Position(13.3393, 52.5053)
    dropoff = Position(13.4014, 52.5478)
    seats = 30
    preferences = {"cat": "AV"}

    clock = Clock()
    booking = Booking(clock, pickup, dropoff, seats, preferences)

    assert booking.seats == seats
    assert booking.pickup == pickup
    assert booking.dropoff == dropoff
    assert booking.preferences == preferences


def test_pending_state():
    clock = Clock()
    booking = Booking(clock, Position(13.4014, 52.5478), Position(13.3393, 52.5053), 3)

    assert booking.is_pending() is True

    with pytest.raises(Exception):
        booking._set_pending()


def test_change_flow():
    clock = Clock()
    booking = Booking(clock, Position(13.4014, 52.5478), Position(13.3393, 52.5053), 3)

    booking.set_matched()
    assert booking.is_matched() is True
    with pytest.raises(Exception):
        booking._set_pending()

    booking.set_waiting_pickup()
    assert booking.is_waiting_pickup() is True
    with pytest.raises(Exception):
        booking.set_matched()

    booking.set_pickup()
    assert booking.is_pickup() is True
    with pytest.raises(Exception):
        booking.set_waiting_pickup()

    booking.set_waiting_dropoff()
    assert booking.is_waiting_dropoff() is True
    with pytest.raises(Exception):
        booking.set_pickup()

    booking.set_dropoff()
    assert booking.is_dropoff() is True
    with pytest.raises(Exception):
        booking.set_waiting_dropoff()


def test_expire():
    clock = Clock()
    booking = Booking(clock, Position(13.4014, 52.5478), Position(13.3393, 52.5053), 3)

    booking.set_expired()

    with pytest.raises(Exception):
        booking.set_matched()


# def test_dispatcher_cancel():
#     clock = Clock()
#     booking = Booking(clock, Position(13.4014, 52.5478), Position(13.3393, 52.5053), 3)

#     booking.set_dispatcher_canceled()
#     assert booking.is_dispatcher_canceled() is True

#     with pytest.raises(Exception):
#         booking.set_matched()

#     with pytest.raises(Exception):
#         booking.set_customer_canceled()


# def test_customer_cancel():
#     clock = Clock()
#     booking = Booking(clock, Position(13.4014, 52.5478), Position(13.3393, 52.5053), 3)

#     booking.set_customer_canceled()
#     assert booking.is_customer_canceled() is True

#     with pytest.raises(Exception):
#         booking.set_matched()

#     with pytest.raises(Exception):
#         booking.set_dispatcher_canceled()


def test_on_state_changed_pending():
    pickup = Position(13.4014, 52.5478)
    dropoff = Position(13.3393, 52.5053)

    clock = Clock()
    booking = Booking(clock, pickup, dropoff, 3)

    event_data = MagicMock()
    event_data.transition = MagicMock()

    # test to pending
    event_data.transition.dest = States.pending.value
    event_data.kwargs = {}

    booking.on_state_changed(event_data)
    assert event_data.kwargs["position"] == pickup.to_dict()
    assert event_data.kwargs["dropoff"] == dropoff.to_dict()


def test_on_state_changed_pickup_position():
    pickup = Position(13.4014, 52.5478)
    dropoff = Position(13.3393, 52.5053)

    clock = Clock()
    booking = Booking(clock, pickup, dropoff, 3)

    event_data = MagicMock()
    event_data.transition = MagicMock()

    for state in (
        States.pending.value,
        States.matched.value,
        States.pickup.value,
        States.expired.value,
        States.waiting_dropoff.value,
        States.waiting_pickup.value,
        States.expired.value,
    ):

        event_data.transition.dest = state
        event_data.kwargs = {}
        booking.on_state_changed(event_data)
        assert event_data.kwargs["position"] == pickup.to_dict()


def test_on_state_changed_pickup_position():
    pickup = Position(13.4014, 52.5478)
    dropoff = Position(13.3393, 52.5053)

    clock = Clock()
    booking = Booking(clock, pickup, dropoff, 3)

    event_data = MagicMock()
    event_data.transition = MagicMock()

    for state in (States.dropoff.value, States.complete.value):

        event_data.transition.dest = state
        event_data.kwargs = {}
        booking.on_state_changed(event_data)

        assert event_data.kwargs["position"] == dropoff.to_dict()
