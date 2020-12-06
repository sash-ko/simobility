from abc import ABC, abstractmethod
from haversine import haversine
import json
from typing import Tuple, Dict
from uuid import uuid4


class BasePosition(ABC):

    def __init__(self):
        self.id = uuid4().hex

    @abstractmethod
    def distance(self, pos) -> float:
        pass

    @property
    @abstractmethod
    def coords(self) -> Tuple:
        pass

    @abstractmethod
    def __eq__(self, other) -> bool:
        pass

    @abstractmethod
    def to_dict(self) -> Dict:
        pass

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return json.dumps(self.to_dict())


class Position(BasePosition):
    """
    lon/lat -> x/y order of coordinates
    """

    def __init__(self, lon, lat):
        """
        Params
        ------

        lon : float
            Longitude

        lat : float
            Latitude
        """

        super().__init__()

        # https://en.wikipedia.org/wiki/Decimal_degrees
        # e.g. the error of precision=6 is ~111 mm
        self.lat = round(lat, 6)
        self.lon = round(lon, 6)

        # max distance between two points to consider them the same
        self._distance_threshold = 0.005

        self._validate()

    def _validate(self):
        if self.lat > 90 or self.lat < -90:
            raise Exception(f"{self.lat} is not correct latitude")
        if self.lon > 180 or self.lon < -180:
            raise Exception(f"{self.lon} is not correct longitude")

    def distance(self, pos) -> float:
        """Haversine distance in km

        Params
        ------

        pos : Position

        distance : float
            Haversine in kilometers
        """

        # haversine expects lat/lon of each point
        return haversine(self.coords[::-1], pos.coords[::-1])

    @property
    def coords(self) -> Tuple[float, float]:
        return (self.lon, self.lat)

    def __eq__(self, other):
        return self.id == other.id or self.distance(other) < self._distance_threshold

    def to_dict(self):
        d = {
            "lat": round(self.lat, 6),
            "lon": round(self.lon, 6)
            # 'id': self.id
        }
        return d

    def __repr__(self):
        return f"Position({self.lon}, {self.lat})"

