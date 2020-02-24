import itertools
import logging
from typing import List, Tuple
import numpy as np
from math import ceil


def linear_approximation(
    pcnt: float, points: List[Tuple[float, float]], segment_distances: List[float]
) -> Tuple[float, float]:
    """ Approximate a coordinates of a point on a route (a sequence of points
    with known distance between them) knowing total distance to the point

    Params
    ------

    distance : float
        Distance to the "approximation" point

    points : list
        List of points, each point is a tuple(x, y)

    segment_distances : list
        Distance between each pair of points

    Example

    Route:
    (1)----(2)--(3)-----(4)

    pcnt = 0.8
    segments = [(1), (2), (3), (4)]
    segment_distances = [4, 2, 5]

    Approximated position of the point:
    (1)----(2)--(3)--[?]---(4)

    total distance = 4 + 2 + 5 = 11
    traveled distance = 11 * 0.8 = 8.8

    position is somewhere between (3) and (4) - total distance 11 and distance
    from (1) to (3) is 6

    remaining distance = 11 - 8.8 = 2.2
    fraction of distance between (3) and (4) is 2.2 / 5 = 0.44

    position = 3 + (4 - 3) * 0.44 = 3.44
    """

    if len(points) == 1:
        return points[0]

    if pcnt > 1:
        raise ValueError("Pcnt cannot be greater than 1")

    acc_distances = list(itertools.accumulate(segment_distances))
    distance = sum(segment_distances) * pcnt

    idx = len(list(itertools.takewhile(lambda i: i < distance, acc_distances)))

    if idx >= len(segment_distances):

        logging.error("Travel distance is longer than a route distance")
        # TODO: figure out why it throws and exception when used with OSRM router
        idx = len(segment_distances) - 1
        # raise InvalidParameter(
        # f'distance is too long: {distance}, max: {acc_distances[-1]}')

    points = points[idx : idx + 2]

    if len(segment_distances) == 1 or idx == 0:
        min_dist = 0
        max_dist = segment_distances[0]
    else:
        min_dist, max_dist = acc_distances[idx - 1 : idx + 1]

    diff = max_dist - min_dist
    if diff:
        pcnt = min((distance - min_dist) / diff, 1)
    else:
        pcnt = 0

    # find a position between two points proportionaly to the traveled time
    x = points[0][0] + (points[1][0] - points[0][0]) * pcnt
    y = points[0][1] + (points[1][1] - points[0][1]) * pcnt

    return x, y


def mins_to_clock_time(time_array, clock):
    """ Convert an array of numbers (time is minutes) to clock time

    Params
    ------

    time_array : np.array
        Array where each item is time in minutes, e.g. duration
        (distance) matrix

    clock : Clock
        Clock used to convert time

    Returns
    -------

    time_array : np.array
        Array with items converted to clock time
    """

    def __to_clock_time(v):
        return ceil(clock.time_to_clock_time(v, "m"))

    to_clock_time_vec = np.vectorize(__to_clock_time)
    time_array = to_clock_time_vec(time_array)
    return time_array

