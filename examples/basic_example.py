import simobility.routers as routers
from simobility.core import Clock
from simobility.core import Fleet
from simobility.core import Vehicle
from simobility.core import Position
from simobility.core import Booking
from simobility.core import Dispatcher
from simobility.core import Itinerary


def create_booking(clock):
    pickup = Position(13.3752, 52.5467)
    dropoff = Position(13.4014, 52.5478)
    return Booking(clock, pickup=pickup, dropoff=dropoff)


def create_fleet(clock):
    # use LinearRouter router to move vehicles
    router = routers.LinearRouter(clock=clock)

    fleet = Fleet(clock, router)

    vehicle = Vehicle(clock)
    fleet.infleet(vehicle, Position(13.4014, 52.5478))

    return fleet


def print_trip_time(vehicle, booking, clock):
    router = routers.LinearRouter(clock=clock)

    eta = router.estimate_duration(booking.pickup, vehicle.position)
    print(f"Pickup in around {round(clock.clock_time_to_seconds(eta) / 60)} minutes")

    eta = eta + router.estimate_duration(booking.pickup, booking.dropoff)
    print(f"Dropoff in around {round(clock.clock_time_to_seconds(eta) / 60)} minutes")


if __name__ == "__main__":

    clock = Clock(
        time_step=10, time_unit="s", starting_time="2020-02-05 12:35:01", initial_time=5
    )
    print(f"Current time {clock.to_datetime()} ({clock.now} clock time)")

    fleet = create_fleet(clock)
    vehicle = fleet.get_online_vehicles()[0]

    booking = create_booking(clock)

    print_trip_time(vehicle, booking, clock)

    print(f'Booking state is "{booking.state.value}"')
    print(f'Vehicle state is "{vehicle.state.value}"')

    # explain vehicle what to do
    itinerary = Itinerary(clock.now, vehicle)
    itinerary.move_to(booking.pickup)
    itinerary.pickup(booking)
    itinerary.move_to(booking.dropoff)
    itinerary.dropoff(booking)

    dispatcher = Dispatcher()
    dispatcher.dispatch(itinerary)

    print(f"Start simulation at {clock.to_datetime()} ({clock.now} clock time)")
    # run simulation - all state changes and movements will happen here
    while not itinerary.is_completed():
        fleet.step()
        dispatcher.step()
        clock.tick()

    print(f"Stop simulation at {clock.to_datetime()} ({clock.now} clock time)")

    print(f'Booking state is "{booking.state.value}"')
    print(f'Vehicle state is "{vehicle.state.value}"')

    fleet.stop_vehicles()
