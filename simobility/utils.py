from shapely.geometry.polygon import Polygon
from shapely.geometry import shape
import json


def read_polygon(file_name: str) -> Polygon:
    """Read polygon fron geojson file and convert to shapely.Geometry"""

    geom = None
    with open(file_name) as f:
        geom = json.load(f)
        geom = shape(geom["features"][0]["geometry"])

    return geom
