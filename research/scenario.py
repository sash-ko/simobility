import json
from shapely.geometry import shape
import logging
import pandas as pd
import math
from datetime import timedelta

from simobility.core import Clock
import simobility.routers as routers
from simobility.core import Fleet
from simobility.core import BookingService
from simobility.core import Dispatcher
import simobility.models as models
from simobility.simulator.simulator import Simulator, Context


def create_demand_model(
    demand_file,
    num_bookings,
    from_datetime,
    offset_minutes,
    clock,
    seed,
    geofence,
    map_matcher,
):

    to_datetime = from_datetime + timedelta(minutes=offset_minutes)

    round_to = clock.to_pandas_units()
    demand = models.DemandFileReplay(
        clock,
        demand_file,
        from_datetime,
        to_datetime,
        round_to,
        num_bookings,
        seed=seed,
        geofence=geofence,
        map_matcher=map_matcher,
    )
    return demand


class DemandWrapper:
    def __init__(self, demand, clock):
        self.demand = demand
        self.clock = clock

    def next(self):
        return self.demand.get_next(pd.to_datetime(self.clock.to_datetime()))


def get_geofence(file_name):
    if file_name:
        with open(file_name) as f:
            return shape(json.load(f)["features"][0]["geometry"])


def create_scenario(config):
    clock = Clock(
        time_step=config["simulation"]["clock_step"],
        time_unit="s",
        starting_time=config["simulation"]["starting_time"],
    )

    geofence = get_geofence(config["geofence"])

    fleet_router = routers.LinearRouter(clock=clock)
    # fleet_router = routers.OSRMRouter(clock=clock, server=OSRM_SERVER)
    logging.info(f"Fleet router {fleet_router}")
    fleet_router = routers.CachingRouter(fleet_router)

    fleet = Fleet(clock, fleet_router)
    models.infleet_geojson(
        clock,
        fleet,
        config["fleet"]["vehicles"],
        config["fleet"]["stations"],
        geofence=geofence,
        seed=config["simulation"]["fleet_seed"],
    )

    max_pending_time = clock.time_to_clock_time(
        config["bookings"]["max_pending_time"], "m"
    )
    booking_service = BookingService(clock, max_pending_time)

    duration_mins = config["simulation"]["duration"]
    duration = clock.time_to_clock_time(duration_mins, "m")
    logging.info(f"Number of simulation steps: {duration}")

    from_datetime = clock.to_datetime()
    demand = create_demand_model(
        config["demand"]["data_file"],
        math.ceil(duration_mins / 60) * config["bookings"]["bookings_per_hour"],
        from_datetime,
        duration_mins,
        clock,
        seed=config["simulation"]["demand_seed"],
        geofence=geofence,
        map_matcher=fleet_router,
    )

    dispatcher = Dispatcher()

    context = Context(clock, fleet, booking_service, dispatcher)
    context.geofence = geofence
    context.duration = duration

    return context, DemandWrapper(demand, clock)
