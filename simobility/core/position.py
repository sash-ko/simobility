from haversine import haversine
import json
from typing import Tuple
from uuid import uuid4


class Position:
    """
    lon/lat -> x/y order of coordinates
    """

    def __init__(self, lon, lat, precision=5):
        """
        Params
        ------

        lon : float
            Longitude

        lat : float
            Latitude

        precision : int
            Precision to route lat and lon coordinates to avoid comparison
            issues
        """

        super().__init__()

        self.id = uuid4().hex

        # https://en.wikipedia.org/wiki/Decimal_degrees
        # e.g. the error of precision=5 is ~1 meter
        self.lat = round(lat, precision)
        self.lon = round(lon, precision)

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
        return self.lat == other.lat and self.lon == other.lon

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_dict(self):
        d = {
            "lat": round(self.lat, 5),
            "lon": round(self.lon, 5)
            # 'id': self.id
        }
        return d

    def __repr__(self):
        return f"Position({self.lon}, {self.lat})"

    def __str__(self):
        return json.dumps(self.to_dict())
