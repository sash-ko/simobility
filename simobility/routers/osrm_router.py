from math import ceil
from typing import Dict, List
import numpy as np
import logging
import requests
from ..core.position import Position
from .route import Route
from .utils import mins_to_clock_time
from .base_router import BaseRouter


class OSRMRouter(BaseRouter):
    r"""
    Router that will query the provided OSRM server for routes. See
    https://github.com/Project-OSRM/osrm-backend for instructions on
    how to set up an OSRM server.

    Usage sample::

    ..highlight:: python
    ..code-block::python

        >>> from .routers.osrm_router import OSRMRouter
        >>> my_router = OSRMRouter(clock=clock, server=server)
    """

    def __init__(self, clock, server: str):
        self.clock = clock
        self.server = server

    def map_match(self, position: Position) -> Position:
        coords = "{},{}".format(*position.coords)
        query = f"{self.server}/nearest/v1/driving/{coords}"
        data = self.request(query, None)
        location = data["waypoints"][0]["location"]
        return Position(*location)

    def calculate_route(self, origin: Position, destination: Position) -> Route:
        """
        Calculate route between 2 points

        Params
        ------

        origin : Position
        destination : Position

        Returns
        -------

        route : Route
        """

        data = _query_osrm(self.server, "route", [origin], [destination])

        geom = data["routes"][0]["geometry"]
        # convert route coordinates to Postion datatypes
        # coordinates = [origin] + [Position(*c) for c in geom["coordinates"]]
        coordinates = [Position(*c) for c in geom["coordinates"]]

        # compute trip duration in "clock" intrinsic units
        duration_minutes = data["routes"][0]["duration"] / 60
        # duration in clock unites
        duration_clock = self.clock.time_to_clock_time(duration_minutes, "m")

        # compute speed in km per clock units
        distance_km = data["routes"][0]["distance"] / 1000

        return Route(
            self.clock.now,
            coordinates,
            duration_clock,
            distance_km,
            origin,
            destination,
        )

    def estimate_duration(self, origin: Position, destination: Position) -> int:
        """ Duration in clock units

        Params
        ------

        origin : Position
        destination : Position

        Returns
        -------

        duration : int
            Trip duration in clock units
        """

        data = _query_osrm(self.server, "table", [origin], [destination])

        if data["durations"][0][0] is None:
            logging.warning("Estimated duration is None")
            return np.iinfo(np.int32).max

        # convert to clock time
        duration_minutes = data["durations"][0][0] / 60
        return ceil(self.clock.time_to_clock_time(duration_minutes, "m"))

    def calculate_distance_matrix(
        self,
        sources: List[Position],
        destinations: List[Position],
        travel_time: bool = True,
    ) -> np.array:
        """ Calculate all-to-all travel time - all source to all destinations.
        Here distance means "distance in time"

        Params
        ------

        sources : list
            List of Positions

        destinations : list
            List of Positions

        Returns
        -------

        distance_matrix : np.array
            All-to-all trip durations (distance in time) in clock units
        """
        if not travel_time:
            raise NotImplementedError

        travel_time = np.zeros([len(sources), len(destinations)])

        if sources and destinations:

            data = _query_osrm(self.server, "table", sources, destinations)

            # convert to minutes
            travel_time = np.array(data["durations"]).astype(np.float)
            # replace None with 0
            idx = np.isnan(travel_time)
            travel_time[idx] = np.iinfo(np.int32).max
            travel_time = travel_time / 60
            travel_time = mins_to_clock_time(travel_time, self.clock)

        return travel_time

    def request(self, path, payload):
        response = requests.get(path)

        if not response.ok:
            logging.error(response.text)
            raise Exception("OSRM Routing error")

        return response.json()


def _query_osrm(server: str, service: str, sources: List, destinations: List) -> Dict:
    """
    Static helper function to form GET request for OSRM backend, make request,
    check for errors, and return pre-parsed data.
    """
    # Form GET request URL string, see
    # https://github.com/Project-OSRM/osrm-backend/blob/master/docs/http.md#example-request-1)

    points = sources + destinations
    coords = ";".join(["{},{}".format(*c.coords) for c in points])
    query = f"{server}/{service}/v1/driving/{coords}"

    if service == "route":
        query = query + "?geometries=geojson"

    elif service == "table":
        source_idx = range(len(sources))
        dest_idx = range(len(sources), len(sources + destinations))
        sources = ";".join(map(str, source_idx))
        destinations = ";".join(map(str, dest_idx))
        query = query + f"?sources={sources}&destinations={destinations}"
        query += "&generate_hints=false"

    else:
        raise NotImplementedError(f"OSRM service {service} not implemented.")

    # Make request to server and parse response
    response = requests.get(query)

    # Catch errors and fail hard
    if not response.status_code == 200:
        logging.error(response.text)
        raise Exception(
            f"Query {query}\nFailed with response {response}, ERROR {response.status_code}"
        )

    return response.json()
