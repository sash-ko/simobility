import simobility.routers as routers
from simobility.core import Clock
from simobility.core import Fleet
from simobility.core import Vehicle
from simobility.core import Position
from simobility.core import Booking
from simobility.core import Dispatcher
from simobility.core import Itinerary


if __name__ == "__main__":

    clock = Clock(
        time_step=10, time_unit="s", starting_time="2020-02-05 12:35:01", initial_time=5
    )
    print(f'Current time {clock.to_datetime()} ({clock.now} clock time)')

    dispatcher = Dispatcher()

    # use LinearRouter router to move vehicles
    router = routers.LinearRouter(clock=clock)
    fleet = Fleet(clock, router)
    vehicle = Vehicle(clock)
    fleet.infleet(vehicle, Position(13.4014, 52.5478))

    pickup = Position(13.3764, 52.5461)
    dropoff = Position(13.4014, 52.5478)
    booking = Booking(clock, pickup=pickup, dropoff=dropoff)

    eta = router.estimate_duration(pickup, vehicle.position)
    print(f'Pickup in around {round(clock.clock_time_to_seconds(eta) / 60)} minutes')

    eta = eta + router.estimate_duration(pickup, dropoff)
    print(f'Dropoff in around {round(clock.clock_time_to_seconds(eta) / 60)} minutes')

    print(f'Booking state is "{booking.state.value}"')
    print(f'Vehicle state is "{vehicle.state.value}"')

    # explain vehicle what to do
    itinerary = Itinerary(clock.now, vehicle)
    itinerary.move_to(pickup)
    itinerary.pickup(booking)
    itinerary.move_to(dropoff)
    itinerary.dropoff(booking)

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
