import simobility.routers as routers
from simobility.core import Clock
from simobility.core import Fleet
from simobility.core import Vehicle
from simobility.core import Position
from simobility.core import Booking
from simobility.core import Dispatcher
from simobility.core import Itinerary
from simobility.core import loggers


def create_booking(clock):
    pickup = Position(13.3752, 52.5467)
    dropoff = Position(13.4014, 52.5478)
    return Booking(clock, pickup=pickup, dropoff=dropoff)


def create_fleet(clock):
    # use LinearRouter router to move vehicles
    router = routers.LinearRouter(clock=clock)

    fleet = Fleet(clock, router)

    vehicle = Vehicle(clock)
    fleet.infleet(vehicle, Position(13.4021, 52.5471))

    return fleet


def print_estimates(vehicle, booking, clock):
    """Print pickup and dropoff ETAs and travel distance"""

    router = routers.LinearRouter(clock=clock)

    route = router.calculate_route(vehicle.position, booking.pickup)
    eta = clock.now + route.duration
    print("\fETAs:")
    print(f"Pickup in {round(clock.clock_time_to_seconds(eta) / 60)} minutes")
    print(f"Distance to pickup {route.distance:.2f} km")

    distance = route.distance
    route = router.calculate_route(booking.pickup, booking.dropoff)

    eta += route.duration
    distance += route.distance

    print(f"Dropoff in {round(clock.clock_time_to_seconds(eta) / 60)} minutes")
    print(f"Distance to dropoff {route.distance:.2f} km")


if __name__ == "__main__":

    loggers.configure_root_logger()

    # create in-memory log handler to be able to access to all
    # state changes after the simulation is over
    simulation_logs = loggers.InMemoryLogHandler()
    _ = loggers.get_simobility_logger(simulation_logs)

    clock = Clock(
        time_step=10, time_unit="s", starting_time="2020-02-05 12:35:01", initial_time=5
    )
    print(f"Current time {clock.to_datetime()} ({clock.now} clock time)")

    fleet = create_fleet(clock)
    vehicle = fleet.get_online_vehicles()[0]

    booking = create_booking(clock)

    print_estimates(vehicle, booking, clock)

    print("\nObject states before simulation:")
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

    print(f"\nStart simulation at {clock.to_datetime()} ({clock.now} clock time)")

    # run simulation - all state changes and movements will happen here
    # the order of steps in important: fleet -> dispatcher -> clock
    while not itinerary.is_completed():
        fleet.step()
        dispatcher.step()
        clock.tick()

    print(f"Stop simulation at {clock.to_datetime()} ({clock.now} clock time)")

    print("\nObject states after simulation:")
    print(f'Booking state is "{booking.state.value}"')
    print(f'Vehicle state is "{vehicle.state.value}"')

    fleet.stop_vehicles()

    print("\nSimulation state changes log:")
    print(simulation_logs.logs)
