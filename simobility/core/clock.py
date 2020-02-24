import datetime
import math
from dateutil import parser
from typing import Optional, List, Union

DEFAULT_DATETIME = "2010-01-01 0:0:1"


class Clock:
    """
    A Clock instance is used to govern time in an Environment. The clock
    time_step is the smallest observable unit of time in a simulation.

    Example:
    >>> from clock import Clock
    >>> clock = Clock(time_unit='m', starting_time='2018-02-02 06:00:00')
    >>> for _ in range(1000):
            clock.tick()
    >>> str(clock.to_datetime())
    '2018-02-02 22:40:00'
    >>> clock.set_clock_time(0)
    >>> str(clock.to_datetime())
    '2018-02-02 06:00:00'
    """

    units = {"s": 60 * 60, "m": 60, "h": 1}

    def __init__(
        self,
        time_step: int = 1,
        time_unit: str = "m",
        starting_time: Union[str, datetime.datetime] = DEFAULT_DATETIME,
        initial_time: int = 0,
    ):
        """
        Params
        ------

        time_step (int)
            number of time_unit's to step with each clock tick

        time_unit (str)
            second(s), minute (m), or hour (h)

        starting_time (str)
            real time corresponding to zero clock time

        initial_time (int)
            initial clock time in clock units
        """
        super().__init__()

        self.configure(
            time_step=time_step,
            time_unit=time_unit,
            starting_time=starting_time,
            initial_time=initial_time,
        )

    def configure(
        self,
        time_step: int = 1,
        time_unit: str = "m",
        starting_time: Union[str, datetime.datetime] = DEFAULT_DATETIME,
        initial_time: int = 0,
    ):

        if time_unit not in self.units:
            raise Exception("Invalid time unit")

        self.clock_time = initial_time
        self.time_step = time_step
        self.time_unit = time_unit
        self.unit = self.units[time_unit]
        self._starting_time = starting_time

        if starting_time and isinstance(starting_time, str):
            self._starting_time = parser.parse(starting_time)

    @property
    def now(self) -> int:
        return self.clock_time

    def to_pandas_units(self) -> str:
        mapping = {"s": "s", "m": "min", "h": "h"}
        return f"{self.time_step}{mapping[self.time_unit]}"

    def tick(self):
        """Increase time by one time step"""
        self.clock_time += 1

    def set_clock_time(self, time: int):
        self.clock_time = time

    @staticmethod
    def get_supported_units() -> List[str]:
        return list(Clock.units.keys())

    def time_to_clock_time(self, time: float, from_time_unit: str) -> int:
        """ Convert time from specified time using time unit to the internal
        """

        if from_time_unit not in self.units:
            raise ValueError("Invalid time unit")

        time = time / self.units[from_time_unit] * self.unit

        # clock time is discrete
        return math.ceil(time / self.time_step)

    def clock_time_to_seconds(self, clock_time: int = None) -> float:
        """Convert time from internal time units to seconds.

        For example:
        # clock with time step - 45 seconds
        clock = Clock(time_step=45, time_units='s')

        # convert 45x45 seconds steps to seconds
        clock.time_to_seconds(45)
        """

        if clock_time == 0:
            return clock_time

        clock_time = clock_time or self.clock_time

        return clock_time * self.time_step * self.units["s"] / self.unit

    def clock_time_to_time(self, clock_time: Optional[int] = None) -> datetime.time:

        clock_time = clock_time or self.clock_time

        hours = self.clock_time / float(self.unit) * self.time_step
        minute = int(hours * 60 - math.floor(hours) * 60)

        hours = math.floor(hours)

        # hour of day
        hour = hours % 24
        time = datetime.time(hour=hour, minute=minute)

        if self._starting_time is not None:
            delta = datetime.timedelta(hours=hours, minutes=minute)
            time = (self._starting_time + delta).time()

        return time

    def to_datetime(self, specific_time: Optional[int] = None) -> datetime.datetime:
        if self._starting_time is None:
            raise ValueError(
                "Cannot convert to datetime since starting point is not defined"
            )

        time_ = self.clock_time
        if specific_time is not None:
            time_ = specific_time

        delta = datetime.timedelta(seconds=self.clock_time_to_seconds(time_))
        return self._starting_time + delta

    def reset(self):
        self.clock_time = 0
