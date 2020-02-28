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
    router = routers.LinearRouter(clock=clock)

    dispatcher = Dispatcher()
    fleet = Fleet(clock, router)

    vehicle = Vehicle(clock)
    fleet.infleet(vehicle, Position(13.4014, 52.5478))

    pickup = Position(13.3764, 52.5461)
    dropoff = Position(13.4014, 52.5478)
    booking = Booking(clock, pickup=pickup, dropoff=dropoff)

    itinerary = Itinerary(clock.now, vehicle)
    itinerary.move_to(pickup)
    itinerary.pickup(booking)
    itinerary.move_to(dropoff)
    itinerary.dropoff(booking)

    dispatcher.dispatch(itinerary)

    print(f"Start simulation at {clock.to_datetime()} ({clock.now} clock time)")
    while not itinerary.is_completed():
        fleet.step()
        dispatcher.step([])
        clock.tick()

    print(f"Stop simulation at {clock.to_datetime()} ({clock.now} clock time)")

    fleet.stop_vehicles()
