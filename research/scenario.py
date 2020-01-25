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
# import simobility.models as models
from simobility.core.tools import ReplayDemand
from simobility.simulator.simulator import Simulator, Context


def create_demand_model(
    config,
    clock,
    map_matcher
):

    from_datetime = clock.to_datetime()
    duration_mins = config["simulation"]["duration"]

    to_datetime = from_datetime + timedelta(minutes=duration_mins)

    num_bookings = math.ceil(duration_mins / 60) * config["bookings"]["bookings_per_hour"]

    round_to = clock.to_pandas_units()
    demand = ReplayDemand(
        clock,
        config["demand"]["data_file"],
        from_datetime,
        to_datetime,
        round_to,
        num_bookings,
        map_matcher=map_matcher,
        seed=config["simulation"].get("demand_seed")
    )
    return demand


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

    fleet_router = routers.LinearRouter(clock=clock)
    # fleet_router = routers.OSRMRouter(clock=clock, server=OSRM_SERVER)
    logging.info(f"Fleet router {fleet_router}")
    fleet_router = routers.CachingRouter(fleet_router)

    fleet = Fleet(clock, fleet_router)
    fleet.infleet_from_geojson(
        config["fleet"]["vehicles"],
        config["fleet"]["stations"],
        geofence_file=config.get("geofence"),
        seed=config["simulation"].get("fleet_seed")
    )

    max_pending_time = clock.time_to_clock_time(
        config["bookings"]["max_pending_time"], "m"
    )
    booking_service = BookingService(clock, max_pending_time)

    demand = create_demand_model(
        config,
        clock=clock,
        map_matcher=fleet_router
    )

    dispatcher = Dispatcher()

    context = Context(clock, fleet, booking_service, dispatcher)
    # context.geofence = geofence

    return context, demand
